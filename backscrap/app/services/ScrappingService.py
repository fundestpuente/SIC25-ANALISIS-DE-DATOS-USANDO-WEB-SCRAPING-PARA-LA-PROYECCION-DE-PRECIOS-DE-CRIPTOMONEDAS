import re
import pandas as pd
import asyncio
from datetime import datetime
from playwright.sync_api import sync_playwright, Error as PlaywrightError

from backscrap.app.repository.ScrappingRepository import ScrappingRepository
from backscrap.app.utils.Global import ResponseUtil, Console
from backscrap.app.utils.broadcaster import broadcaster
import json

class ScrappingService:
    """
    Servicio encargado de orquestar las tareas de web scraping,
    procesar los datos y persistirlos usando el repositorio.
    """
    COL_NAMES = ["row", "symbol", "name", "price", "change24h", "volume24h", "marketCap"]

    def __init__(self, repository: ScrappingRepository):
        """Inicializa el servicio con una instancia de ScrappingRepository."""
        self.repository = repository
        # Mapeo de fuentes a sus respectivas funciones de scraping
        self._scraping_functions = {
            "CoinGecko": self._scrape_coingecko,
            "Coinmarketcap": self._scrape_coinmarketcap,
            #"WorldCoinIndex": self._scrape_worldcoinindex,
        }

    def _run_playwright_sync(self, url: str, scraper_func, **kwargs) -> pd.DataFrame:
        """
        Ejecuta una sesión síncrona de Playwright. Esta función está diseñada
        para ser llamada en un hilo separado para no bloquear el event loop de asyncio.
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                page.set_default_timeout(60000)
                page.goto(url, wait_until="load")
                
                result_df = scraper_func(page, **kwargs)
                return result_df
        except PlaywrightError as e:
            # Captura errores específicos
            Console.error(f"Error de Playwright en {url}: {e}")
            return pd.DataFrame(columns=self.COL_NAMES)
        except Exception as e:
            Console.error(f"Error inesperado en la función de scraping para {url}: {e}")
            return pd.DataFrame(columns=self.COL_NAMES)


    def _scrape_coingecko(self) -> pd.DataFrame:
        """Lógica de scraping para CoinGecko."""
        url = "https://www.coingecko.com/"
        Console.log(f"Iniciando scraping para {url}...")

        def scraper_logic(page):
            # Coingecko requiere esperar un poco más
            page.wait_for_timeout(5000)

            # Selector de las filas (tbody tr)
            rows = page.locator(".gecko-homepage-coin-table tbody tr").all()

            #print(f"registros {len(rows)}, {rows}")

            data = []
            for i, row_locator in enumerate(rows[:15]):  # Limitar a top 15
                try:
                    cells = row_locator.locator("td").all()
                    if len(cells) < 10:  # Mínimo de celdas requerido
                        continue

                    # El código R indica que el símbolo se extrae de ".tw-block"
                    symbol = row_locator.locator("div.tw-block").inner_text().strip()
                    name_container = row_locator.locator("div.tw-text-gray-700.tw-font-semibold.tw-text-sm.tw-leading-5")

                    name = name_container.evaluate("node => node.childNodes[0].textContent.trim()")
                    #print(f"moneda: {symbol} - {name}")

                    # Columna 5 (Price)
                    price_raw = cells[4].inner_text()
                    # Columna 7 (Change 24h)
                    change24h_raw = cells[6].inner_text()
                    # Columna 10 (Volume 24h)
                    volume24h_raw = cells[9].inner_text()
                    # Columna 11 (Market Cap)
                    market_cap_raw = cells[10].inner_text()
                    # El código R limpia price
                    price = re.sub(r'[^\d\.,$]+', '', price_raw).replace("$", "").replace(",", "")

                    # En Playwright, buscamos el signo en el texto o asumimos el formato de CoinGecko.
                    # Asumiremos que el signo ya está incluido en change24h_raw, o lo agregamos si es necesario.
                    if not re.match(r'[+-]', change24h_raw):
                        # Buscamos la clase para el signo (más robusto)
                        # Up/Down span is in cells[6]
                        icon_class = cells[6].locator("span").get_attribute("class")
                        signo = "+" if "up" in icon_class else "-" if "down" in icon_class else ""
                        change24h = signo + re.sub(r'[^\d\.,%]', '', change24h_raw)
                    else:
                        change24h = re.sub(r'[^\d\.,%+-]', '', change24h_raw)

                    # Limpieza de Market Cap y Volumen
                    market_cap = re.sub(r'[^\d\.,]', '', market_cap_raw).replace(",", "")
                    volume24h = re.sub(r'[^\d\.,]', '', volume24h_raw).replace(",", "")
                    change24h = change24h.replace("%", "")

                    data.append({
                        "row": i + 1,
                        "symbol": symbol.strip(),
                        "name": name.strip(),
                        "price": price.strip(),
                        "change24h": change24h.strip(),
                        "volume24h": volume24h.strip(),
                        "marketCap": market_cap.strip()
                    })
                except Exception as e:
                    print(f"Error procesando fila {i + 1} en CoinGecko: {e}")
                    continue
            return pd.DataFrame(data, columns=self.COL_NAMES)




        return self._run_playwright_sync(url, scraper_logic)

    def _scrape_coinmarketcap(self) -> pd.DataFrame:
        """Lógica de scraping para Coinmarketcap."""
        url = "https://coinmarketcap.com/es/"
        Console.log(f"Iniciando scraping para {url}...")
        def scraper_logic(page):
            # Scroll para cargar datos. El código R usa 2 scrolls al final de la página.
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(3000)

            # Selector de la tabla principal
            # sc-7e3c705d-3 keBvNC cmc-table
            table_locator = page.locator("table.cmc-table")  # Selector actualizado de la tabla
            rows = table_locator.locator("tbody tr").all()

            # print(f"items {len(rows)}, {rows}")

            data = []
            for i, row_locator in enumerate(rows[:15]):  # Limitar a top 15
                try:
                    # El símbolo y el nombre están en la misma celda, separamos el símbolo
                    symbol = row_locator.locator(".coin-item-symbol").inner_text()

                    name = row_locator.locator(".coin-item-name").inner_text()

                    # Price (celda 4)
                    price_raw = row_locator.locator("td:nth-child(4)").inner_text()

                    # Cambio 24h (celda 6)
                    change24h_locator = row_locator.locator("td:nth-child(6)")
                    change24h_percent = change24h_locator.inner_text()

                    # Signo: buscamos la clase del ícono
                    icon_class = change24h_locator.locator("span[class*='icon-Caret']").get_attribute("class")
                    signo = "+" if "icon-Caret-up" in icon_class else "-" if "icon-Caret-down" in icon_class else ""
                    change24h = signo + change24h_percent

                    # Market Cap (celda 7)
                    market_cap_raw = row_locator.locator("td:nth-child(8)").inner_text()

                    # Volumen 24h (celda 8) - Esto puede variar, Coinmarketcap suele tener una columna de volumen 24h y otra de volumen/marketCap
                    # El código R toma el valor de ".font_weight_500" para volumen.
                    volume24h_raw = row_locator.locator(".font_weight_500").first.inner_text()

                    # Limpieza (remplazando , por . si es necesario y quitando chars no numéricos)
                    price = re.sub(r'[^\d\.,]', '', price_raw).replace(".", "").replace(",", ".")
                    market_cap = re.sub(r'[^\d\.,]', '', market_cap_raw).replace(",", "")
                    volume24h = re.sub(r'[^\d\.,]', '', volume24h_raw).replace(",", "")
                    change24h = change24h.replace("%", "")

                    data.append({
                        "row": i + 1,
                        "symbol": symbol.strip(),
                        "name": name.strip(),
                        "price": price.strip(),
                        "change24h": change24h.strip(),
                        "volume24h": volume24h.strip(),
                        "marketCap": market_cap.strip()
                    })
                except Exception as e:
                    print(f"Error procesando fila {i + 1} en Coinmarketcap: {e}")
                    continue
            return pd.DataFrame(data, columns=self.COL_NAMES)

        return self._run_playwright_sync(url, scraper_logic)

    def _scrape_worldcoinindex(self) -> pd.DataFrame:
        """Lógica de scraping para WorldCoinIndex."""
        url = "https://www.worldcoinindex.com"
        Console.log(f"Iniciando scraping para {url}...")
        def scraper_logic(page):
            page.wait_for_timeout(5000)

            # El código R usa #myTable
            table_locator = page.locator("#myTable").first
            rows = table_locator.locator("tbody tr").all()

            data = []
            for i, row_locator in enumerate(rows[:15]):  # Limitar a top 15
                try:
                    cells = row_locator.locator("td").all()
                    if len(cells) < 12:
                        continue

                    # Columna 4 (Symbol)
                    symbol = cells[3].inner_text().strip()
                    name = cells[2].inner_text().strip()
                    # Columna 5 (Price)
                    price_raw = cells[4].inner_text()
                    # Columna 6 (Change 24h)
                    change24h_raw = cells[5].inner_text()
                    # Columna 10 (Volume 24h)
                    volume24h_raw = cells[9].inner_text()
                    # Columna 12 (Market Cap)
                    market_cap_raw = cells[11].inner_text()

                    # Limpieza (el código hace limpieza de espacios en volume24h)
                    price = re.sub(r'[^\d\.,]', '', price_raw)
                    change24h = re.sub(r'[\s]+', '', change24h_raw)
                    volume24h = re.sub(r'[^\d\.,]', '', volume24h_raw)
                    market_cap = re.sub(r'[^\d\.,]', '', market_cap_raw)

                    data.append({
                        "row": i + 1,
                        "symbol": symbol.strip(),
                        "name": name,
                        "price": price.strip(),
                        "change24h": change24h.strip(),
                        "volume24h": volume24h.strip(),
                        "marketCap": market_cap.strip()
                    })
                except Exception as e:
                    print(f"Error procesando fila {i + 1} en WorldCoinIndex: {e}")
                    continue
            return pd.DataFrame(data, columns=self.COL_NAMES)

        return self._run_playwright_sync(url, scraper_logic)

    # --- Métodos Públicos del Servicio ---

    def get_available_sources(self) -> list[str]:
        """Devuelve una lista de las fuentes de scraping disponibles."""
        Console.log("Servicio solicitado para obtener las fuentes de scraping disponibles.")
        return list(self._scraping_functions.keys())

    async def run_scraping_and_save(self, source: str):
        """
        Ejecuta una tarea de scraping para una fuente dada, la procesa y la guarda en la BD.
        Este método es asíncrono y delega el trabajo síncrono a un hilo.
        """
        if source not in self._scraping_functions:
            return ResponseUtil.error(f"La fuente '{source}' no es válida.")

        try:
            scraper_method = self._scraping_functions[source]
            
            # Ejecuta la función de scraping síncrona en un hilo separado
            loop = asyncio.get_running_loop()
            df = await loop.run_in_executor(None, scraper_method)

            if df.empty:
                return ResponseUtil.warning(f"No se obtuvieron datos de {source}.")

            # Prepara los datos para guardarlos
            records = df.to_dict(orient='records')
            timestamp = datetime.now()
            
            # Llama al repositorio para guardar los datos
            # (Asumiendo que el repositorio tiene un método `save_scrapping_results`)
            response = await self.repository.save_scrapping_results(source, timestamp, records)
            
            # Verifica el estado de la respuesta del repositorio antes de imprimir el log
            if response.status == 2: # 2 es el código para 'success' en tu ResponseUtil
                message = f"Éxito: Se guardaron {len(records)} registros de {source}."
                Console.log(message)
                await broadcaster.publish(
                    channel="scraping_events", 
                    message=json.dumps({"status": "SUCCESS", "source": source, "message": message})
                )
            else:
                await broadcaster.publish(
                    channel="scraping_events", 
                    message=json.dumps({"status": "FAILURE", "source": source, "message": response.message})
                )
            return response # La tarea en segundo plano termina aquí

        except Exception as e:
            Console.error(f"Error inesperado durante el scraping de {source}: {e}")
            await broadcaster.publish(channel="scraping_events", message=json.dumps({"status": "ERROR", "source": source, "message": str(e)}))
            return ResponseUtil.error(f"Ocurrió un error inesperado: {str(e)}")

    async def get_results(self, source: str = None):
        """
        Obtiene los resultados de scraping guardados, opcionalmente filtrados por fuente.
        """
        Console.log(f"Servicio solicitado para obtener resultados de la fuente: {source or 'todas'}")
        try:
            response = await self.repository.get_scrapping_results(source)
            return response
        except Exception as e:
            Console.error(f"Error en el servicio al obtener resultados: {e}")
            return ResponseUtil.error(f"Ocurrió un error inesperado en el servicio: {str(e)}")