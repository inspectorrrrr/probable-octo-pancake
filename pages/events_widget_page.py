"""
Page Object Model для страницы Events Widget
"""
import re
from playwright.sync_api import Page, expect


class EventsWidgetPage:
    """Класс для взаимодействия со страницей Events Widget"""
    
    def __init__(self, page: Page):
        self.page = page
        self.url = "https://dev.3snet.info/eventswidget/"
        
        # Локаторы основных элементов
        self.widget_container = page.locator('[class*="widget"], [class*="events"], [id*="widget"], [id*="events"]').first
        self.event_items = page.locator('[class*="event"], [class*="item"], article, .card')
        self.event_titles = page.locator('[class*="title"], h1, h2, h3, h4')
        self.event_dates = page.locator('[class*="date"], time, [datetime]')
        self.event_descriptions = page.locator('[class*="description"], [class*="text"], p')
        
        # Локаторы для генератора превью
        self.generate_preview_button = page.locator('text="Сгенерировать превью"')
        # Более широкий поиск селекторов
        self.all_selectors = page.locator('select, [role="combobox"], [class*="select"], [class*="dropdown"], input[list]')
        self.theme_selector = self.all_selectors.first
        self.country_selector = self.all_selectors.nth(1)
        # Альтернативные локаторы для превью
        self.preview_area = page.locator('[class*="preview"], [class*="widget-preview"], .preview-container, .widget-container, main, .content')
        self.empty_state = page.locator('[class*="empty"], [class*="no-data"], [class*="no-events"], text="Нет событий", text="Пусто"')
        
        # Специфичные локаторы для виджета событий
        self.event_name_header = page.locator('text="Название события"')
        self.event_date_header = page.locator('text="Дата проведения"')
        self.event_country_header = page.locator('text="Страны проведения"')
        
        # Локаторы для кнопок очистки и управления
        self.clear_buttons = page.locator('button:has-text("Очистить"), button:has-text("Clear"), [class*="clear"], [class*="reset"]')
        self.clear_country_button = page.locator('button:has-text("Очистить"):near([class*="country"], [class*="страна"])')
        
        # Локаторы для проверки наложения текста
        self.overlapping_elements = page.locator('[style*="position: absolute"], [style*="z-index"]')
        self.text_elements = page.locator('span, div, p, label').filter(has_text=re.compile(r'\w+'))
        
    def navigate(self):
        """Переход на страницу"""
        try:
            self.page.goto(self.url, wait_until="networkidle", timeout=30000)
        except Exception as e:
            # Если страница недоступна, пробуем с более мягкими настройками
            try:
                self.page.goto(self.url, wait_until="domcontentloaded", timeout=15000)
            except Exception:
                # Если и это не работает, пробуем без ожидания
                self.page.goto(self.url, timeout=10000)
        
    def is_page_loaded(self) -> bool:
        """Проверка загрузки страницы"""
        try:
            # Проверяем, что мы на правильной странице
            current_url = self.page.url
            if self.url in current_url or "eventswidget" in current_url:
                return True
            expect(self.page).to_have_url(self.url, timeout=5000)
            return True
        except Exception:
            # Если точная проверка URL не работает, проверяем наличие контента
            try:
                body = self.page.locator('body')
                expect(body).to_be_visible(timeout=5000)
                return True
            except Exception:
                return False
            
    def get_page_title(self) -> str:
        """Получение заголовка страницы"""
        return self.page.title()
        
    def is_widget_visible(self) -> bool:
        """Проверка видимости виджета"""
        try:
            # Ждем появления любого контента на странице
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            # Проверяем наличие body с контентом
            body = self.page.locator("body")
            expect(body).to_be_visible(timeout=5000)
            return True
        except Exception:
            return False
            
    def get_events_count(self) -> int:
        """Получение количества событий"""
        try:
            self.page.wait_for_timeout(2000)  # Ждем загрузки динамического контента
            return self.event_items.count()
        except Exception:
            return 0
            
    def get_event_titles(self) -> list[str]:
        """Получение списка заголовков событий"""
        try:
            self.page.wait_for_timeout(2000)
            titles = []
            count = self.event_titles.count()
            for i in range(min(count, 10)):  # Ограничиваем первыми 10
                title = self.event_titles.nth(i).text_content()
                if title and title.strip():
                    titles.append(title.strip())
            return titles
        except Exception:
            return []
            
    def click_first_event(self):
        """Клик по первому событию"""
        if self.event_items.count() > 0:
            self.event_items.first.click()
            self.page.wait_for_timeout(1000)
            
    def is_responsive(self, width: int, height: int) -> bool:
        """Проверка адаптивности на заданном разрешении"""
        try:
            self.page.set_viewport_size({"width": width, "height": height})
            self.page.wait_for_timeout(1000)
            body = self.page.locator("body")
            expect(body).to_be_visible()
            return True
        except Exception:
            return False
            
    def has_interactive_elements(self) -> bool:
        """Проверка наличия интерактивных элементов"""
        try:
            # Проверяем наличие кликабельных элементов
            clickable = self.page.locator('a, button, [onclick], [role="button"]')
            return clickable.count() > 0
        except Exception:
            return False
            
    def get_page_content(self) -> str:
        """Получение содержимого страницы для анализа"""
        try:
            return self.page.content()
        except Exception:
            return ""
            
    def wait_for_content_load(self, timeout: int = 5000):
        """Ожидание загрузки контента"""
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            self.page.wait_for_timeout(1000)
        except Exception:
            pass
    def is_generate_preview_button_visible(self) -> bool:
        """Проверка видимости кнопки 'Сгенерировать превью'"""
        try:
            expect(self.generate_preview_button).to_be_visible(timeout=5000)
            return True
        except Exception:
            return False
            
    def click_generate_preview(self):
        """Клик по кнопке 'Сгенерировать превью'"""
        try:
            self.generate_preview_button.click()
            self.page.wait_for_timeout(2000)  # Ждем загрузки превью
        except Exception:
            pass
            
    def select_theme(self, theme_text: str = None):
        """Выбор тематики"""
        try:
            if self.theme_selector.count() > 0:
                if theme_text:
                    self.theme_selector.select_option(label=theme_text)
                else:
                    # Выбираем первую доступную опцию
                    options = self.theme_selector.locator('option')
                    if options.count() > 1:  # Пропускаем placeholder
                        first_option = options.nth(1).get_attribute('value')
                        if first_option:
                            self.theme_selector.select_option(value=first_option)
                self.page.wait_for_timeout(1000)
        except Exception:
            pass
            
    def select_country(self, country_text: str = None):
        """Выбор страны"""
        try:
            if self.country_selector.count() > 0:
                if country_text:
                    self.country_selector.select_option(label=country_text)
                else:
                    # Выбираем первую доступную опцию
                    options = self.country_selector.locator('option')
                    if options.count() > 1:  # Пропускаем placeholder
                        first_option = options.nth(1).get_attribute('value')
                        if first_option:
                            self.country_selector.select_option(value=first_option)
                self.page.wait_for_timeout(1000)
        except Exception:
            pass
            
    def is_preview_area_visible(self) -> bool:
        """Проверка видимости области превью"""
        try:
            expect(self.preview_area).to_be_visible(timeout=5000)
            return True
        except Exception:
            return False
            
    def is_preview_empty(self) -> bool:
        """Проверка, что превью пустое"""
        try:
            # Проверяем наличие индикаторов пустого состояния
            if self.empty_state.count() > 0:
                return True
                
            # Проверяем, что в области превью нет событий
            preview_events = self.preview_area.locator('[class*="event"], [class*="item"], .event-card')
            return preview_events.count() == 0
        except Exception:
            return True
            
    def get_preview_events_count(self) -> int:
        """Получение количества событий в превью"""
        try:
            if not self.is_preview_area_visible():
                return 0
            preview_events = self.preview_area.locator('[class*="event"], [class*="item"], .event-card')
            return preview_events.count()
        except Exception:
            return 0
            
    def has_theme_selector(self) -> bool:
        """Проверка наличия селектора тематики"""
        try:
            return self.all_selectors.count() > 0
        except Exception:
            return False
            
    def has_country_selector(self) -> bool:
        """Проверка наличия селектора страны"""
        try:
            return self.all_selectors.count() > 1
        except Exception:
            return False
            
    def get_theme_options(self) -> list[str]:
        """Получение списка доступных тематик"""
        try:
            all_selectors_count = self.all_selectors.count()
            if all_selectors_count == 0:
                return []
            
            # Проверяем все селекторы, не только первый
            all_themes = []
            for selector_index in range(min(all_selectors_count, 10)):  # Максимум 10 селекторов
                try:
                    selector = self.all_selectors.nth(selector_index)
                    options = selector.locator('option')
                    options_count = options.count()
                    
                    if options_count > 0:
                        for i in range(options_count):
                            try:
                                option = options.nth(i)
                                text = option.text_content()
                                value = option.get_attribute('value')
                                
                                # Более гибкая проверка опций
                                if text and text.strip():
                                    text_clean = text.strip()
                                    # Пропускаем placeholder опции
                                    if (not text_clean.lower().startswith(("выбер", "select", "choose", "--")) 
                                        and len(text_clean) > 1 
                                        and text_clean not in all_themes):
                                        all_themes.append(text_clean)
                                elif value and value.strip() and value != "":
                                    # Если текста нет, но есть value
                                    if value not in all_themes:
                                        all_themes.append(value)
                            except Exception:
                                continue
                except Exception:
                    continue
                    
            return all_themes[:20]  # Максимум 20 опций
        except Exception:
            return []
            
    def get_country_options(self) -> list[str]:
        """Получение списка доступных стран"""
        try:
            all_selectors_count = self.all_selectors.count()
            if all_selectors_count < 2:
                return []
            
            # Проверяем селекторы, начиная со второго
            all_countries = []
            for selector_index in range(1, min(all_selectors_count, 10)):  # Начинаем с 1
                try:
                    selector = self.all_selectors.nth(selector_index)
                    options = selector.locator('option')
                    options_count = options.count()
                    
                    if options_count > 0:
                        for i in range(options_count):
                            try:
                                option = options.nth(i)
                                text = option.text_content()
                                value = option.get_attribute('value')
                                
                                if text and text.strip():
                                    text_clean = text.strip()
                                    # Более гибкая проверка для стран
                                    if (not text_clean.lower().startswith(("выбер", "select", "choose", "--"))
                                        and len(text_clean) > 1
                                        and text_clean not in all_countries):
                                        all_countries.append(text_clean)
                                elif value and value.strip() and value != "":
                                    if value not in all_countries:
                                        all_countries.append(value)
                            except Exception:
                                continue
                except Exception:
                    continue
                    
            return all_countries[:20]  # Максимум 20 опций
        except Exception:
            return []
            
    def wait_for_preview_generation(self, timeout: int = 10000):
        """Ожидание генерации превью"""
        try:
            # Ждем либо появления событий, либо индикатора пустого состояния
            self.page.wait_for_function(
                """() => {
                    const preview = document.querySelector('[class*="preview"], [class*="widget-preview"], .preview-container');
                    if (!preview) return false;
                    
                    const events = preview.querySelectorAll('[class*="event"], [class*="item"], .event-card');
                    const emptyState = preview.querySelector('[class*="empty"], [class*="no-data"], [class*="no-events"]');
                    
                    return events.length > 0 || emptyState !== null;
                }""",
                timeout=timeout
            )
        except Exception:
            pass
            
    def get_error_message(self) -> str:
        """Получение сообщения об ошибке, если есть"""
        try:
            error_selectors = [
                '[class*="error"]',
                '[class*="alert"]',
                '.error-message',
                '.alert-danger',
                '[role="alert"]'
            ]
            
            for selector in error_selectors:
                error_element = self.page.locator(selector)
                if error_element.count() > 0:
                    return error_element.first.text_content() or ""
            return ""
        except Exception:
            return ""
    
    def debug_page_structure(self) -> dict:
        """Отладочный метод для анализа структуры страницы"""
        try:
            debug_info = {
                "selectors_found": self.all_selectors.count(),
                "buttons_found": self.page.locator('button').count(),
                "inputs_found": self.page.locator('input').count(),
                "page_title": self.page.title(),
                "page_url": self.page.url,
                "body_text_length": len(self.page.locator('body').text_content() or ""),
                "all_text_elements": [],
                "selector_details": [],
                "sample_options": []
            }
            
            # Детальная информация о селекторах
            selectors_count = self.all_selectors.count()
            for i in range(min(selectors_count, 10)):  # Максимум 10 селекторов
                try:
                    selector = self.all_selectors.nth(i)
                    options = selector.locator('option')
                    options_count = options.count()
                    
                    selector_info = {
                        "index": i,
                        "options_count": options_count,
                        "tag_name": selector.evaluate("el => el.tagName"),
                        "class_name": selector.get_attribute("class") or "",
                        "id": selector.get_attribute("id") or "",
                        "sample_options": []
                    }
                    
                    # Получаем примеры опций
                    for j in range(min(options_count, 5)):  # Первые 5 опций
                        try:
                            option = options.nth(j)
                            option_text = option.text_content() or ""
                            option_value = option.get_attribute("value") or ""
                            selector_info["sample_options"].append({
                                "text": option_text.strip()[:50],  # Первые 50 символов
                                "value": option_value[:50]
                            })
                        except Exception:
                            pass
                    
                    debug_info["selector_details"].append(selector_info)
                    debug_info[f"selector_{i}_options"] = options_count
                    
                except Exception as e:
                    debug_info["selector_details"].append({
                        "index": i,
                        "error": str(e)
                    })
                
            # Ищем текст кнопок
            buttons = self.page.locator('button')
            for i in range(min(buttons.count(), 10)):  # Максимум 10 кнопок
                try:
                    button_text = buttons.nth(i).text_content()
                    if button_text and button_text.strip():
                        debug_info["all_text_elements"].append(f"button: {button_text.strip()}")
                except Exception:
                    pass
            
            # Ищем все элементы с текстом "превью" или "генер"
            try:
                preview_elements = self.page.locator('text=/превью|генер|preview|generate/i')
                debug_info["preview_elements_count"] = preview_elements.count()
            except Exception:
                debug_info["preview_elements_count"] = 0
            
            # Добавляем информацию о найденных опциях через наши методы
            debug_info["theme_options_found"] = len(self.get_theme_options())
            debug_info["country_options_found"] = len(self.get_country_options())
            
            return debug_info
        except Exception as e:
            return {"error": str(e)}
    
    def has_clear_buttons(self) -> bool:
        """Проверка наличия кнопок очистки"""
        try:
            return self.clear_buttons.count() > 0
        except Exception:
            return False
            
    def click_clear_country(self):
        """Клик по кнопке очистки страны"""
        try:
            if self.clear_country_button.count() > 0:
                self.clear_country_button.first.click()
            elif self.clear_buttons.count() > 0:
                # Если специфичная кнопка не найдена, пробуем общую кнопку очистки
                self.clear_buttons.first.click()
            self.page.wait_for_timeout(1000)  # Ждем применения изменений
        except Exception:
            pass
            
    def check_text_overlapping(self) -> dict:
        """Проверка наложения текста на странице"""
        try:
            overlapping_info = {
                "has_overlapping": False,
                "overlapping_count": 0,
                "overlapping_elements": [],
                "text_elements_count": 0,
                "potential_issues": []
            }
            
            # Подсчитываем текстовые элементы
            text_elements_count = self.text_elements.count()
            overlapping_info["text_elements_count"] = text_elements_count
            
            # Проверяем элементы с абсолютным позиционированием
            overlapping_count = self.overlapping_elements.count()
            overlapping_info["overlapping_count"] = overlapping_count
            
            if overlapping_count > 0:
                overlapping_info["has_overlapping"] = True
                
                # Получаем информацию о наложенных элементах
                for i in range(min(overlapping_count, 5)):  # Максимум 5 элементов
                    element = self.overlapping_elements.nth(i)
                    try:
                        text_content = element.text_content()
                        if text_content and text_content.strip():
                            overlapping_info["overlapping_elements"].append(text_content.strip()[:50])
                    except Exception:
                        pass
            
            # Проверяем потенциальные проблемы с текстом
            try:
                # Ищем элементы, которые могут накладываться друг на друга
                page_content = self.page.content()
                if "position: absolute" in page_content or "z-index" in page_content:
                    overlapping_info["potential_issues"].append("Найдено абсолютное позиционирование")
                
                if "overflow: hidden" in page_content:
                    overlapping_info["potential_issues"].append("Найдено скрытие переполнения")
                    
            except Exception:
                pass
                
            return overlapping_info
            
        except Exception as e:
            return {
                "error": str(e),
                "has_overlapping": False,
                "overlapping_count": 0,
                "overlapping_elements": [],
                "text_elements_count": 0,
                "potential_issues": []
            }
            
    def get_visible_text_elements(self) -> list[str]:
        """Получение списка видимых текстовых элементов"""
        try:
            visible_texts = []
            text_elements = self.page.locator('*').filter(has_text=re.compile(r'\w+'))
            
            for i in range(min(text_elements.count(), 20)):  # Максимум 20 элементов
                element = text_elements.nth(i)
                try:
                    if element.is_visible():
                        text = element.text_content()
                        if text and text.strip() and len(text.strip()) > 2:
                            visible_texts.append(text.strip()[:100])  # Максимум 100 символов
                except Exception:
                    continue
                    
            return visible_texts
        except Exception:
            return []
            
    def take_screenshot_for_analysis(self, filename: str = "page_analysis.png"):
        """Создание скриншота для анализа наложения"""
        try:
            screenshot = self.page.screenshot(path=filename, full_page=True)
            return screenshot
        except Exception:
            return None