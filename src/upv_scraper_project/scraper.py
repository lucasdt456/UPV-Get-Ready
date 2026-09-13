import random
import time
from urllib.parse import urljoin

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from . import constants


class UPVScraper:
    def __init__(self, centre):
        self.centre_name = centre
        self.centre = constants.ABBREVIATIONS_CENTRES[centre]

    def obtain_titulation(self) -> dict:
        titulations = {}
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # the scraping start in: https://www.upv.es/perfiles/estudiante/todo-sobre-titulaciones-es.html
            url = f"https://www.upv.es/pls/oalu/SIC_PLA.LisTitulaciones?P_CEN={self.centre}&p_tipo=plan&p_idioma=c&P_VISTA=&P_NAVEGA="

            time.sleep(random.uniform(1, 3))

            try:
                page.goto(url, wait_until="domcontentloaded")
                second_tbody = page.locator("tbody").nth(1)
                second_tbody.wait_for(state="visible", timeout=10000)

                if second_tbody.count() == 0:
                    browser.close()
                    return "No second <tbody>"

                all_rows = second_tbody.locator("tr").all()

                for row in all_rows:
                    cells = row.locator("td").all()

                    if len(cells) >= 2:
                        titulation = cells[1].inner_text().strip()
                        link = cells[1].locator("a")
                        href_relative = link.get_attribute("href")

                        if titulation and href_relative:
                            url = urljoin(page.url, href_relative)
                            titulations[titulation] = url

            except Exception as e:
                print("Error in scraping: ", e)

            finally:
                browser.close()
        return titulations

    def obtain_course(
        self,
        # titulation_clicked="Grado en Inteligencia Artificial",
        url: str,
    ) -> dict:
        years = {}
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            time.sleep(random.uniform(1, 3))

            try:
                page.goto(url, wait_until="domcontentloaded")

                links_to_url_year = page.locator("td.alignleft.texto_baseG b a")
                try:
                    links_to_url_year.first.wait_for(state="visible", timeout=10000)
                except PlaywrightTimeoutError:
                    print("No found the link in the table")
                    return {}

                for link in links_to_url_year.all():
                    year = link.inner_text().strip()
                    href_relative = link.first.get_attribute("href")

                    if year and href_relative:
                        url = urljoin(page.url, href_relative)
                        years[year] = url

            except Exception as e:
                print("Error in scraping: ", e)

            finally:
                browser.close()
        return years

    def extract_subjects(
        self,
        course_url: str,
    ) -> dict:
        subjects = {}
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            time.sleep(random.uniform(1, 3))

            try:
                page.goto(course_url, wait_until="domcontentloaded")

                second_tbody = page.locator("tbody").nth(1)
                try:
                    second_tbody.wait_for(state="visible", timeout=10000)
                except PlaywrightTimeoutError:
                    print("Not found the <tbody>")
                    return {}

                if second_tbody.count() == 0:
                    browser.close()
                    return "No second <tbody>"

                all_rows = second_tbody.locator("tr").all()

                for row in all_rows:
                    cells = row.locator("td")

                    if cells.count() < 5:
                        continue

                    link_elem = row.locator("td:nth-child(1) a").first
                    if link_elem.count() == 0:
                        continue

                    subject_code_text = link_elem.inner_text().strip()
                    href_relative = link_elem.get_attribute("href")
                    subject_elem = row.locator("td:nth-child(2)").first
                    subject = subject_elem.inner_text().strip()
                    character = (
                        row.locator("td:nth-child(3)").first.inner_text().strip()
                    )
                    semester = row.locator("td:nth-child(4)").first.inner_text().strip()
                    credits = row.locator("td:nth-child(5)").first.inner_text().strip()

                    # print(subject_code_text, subject, href_relative)
                    url = urljoin(page.url, href_relative) if href_relative else ""
                    subjects[subject] = {
                        "code": subject_code_text,
                        "character": character,
                        "semester": semester,
                        "credits": credits,
                        "url": url,
                    }

                # return json.dumps(self._subjects, indent=4)

            except Exception as e:
                print("Error in scraping: ", e)

            finally:
                browser.close()
        return subjects

    def extract_subjects_teaching_guide(
        self, subjects: dict, titulation: str, year: str
    ) -> dict:
        updated_subjects = subjects.copy()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            time.sleep(random.uniform(1, 3))

            for subject_name, subject_data in updated_subjects.items():
                subject_url = subject_data.get("url")

                if not subject_url:
                    print("subject doesn't have url")
                    continue

                try:
                    page.goto(subject_url, wait_until="domcontentloaded")

                    button_full_teaching_guide = page.locator(
                        "a", has_text="Resumen completo guía docente"
                    ).first

                    if button_full_teaching_guide.count() > 0:
                        # print(f"{subject_name} -> Have button")
                        button_full_teaching_guide.click()
                        page.wait_for_load_state("domcontentloaded")

                        all_text = page.locator("body").inner_text()
                        updated_subjects[subject_name]["teaching_guide"] = (
                            all_text.strip()
                        )

                    else:
                        # print(f"{subject_name} -> Don't have button")
                        updated_subjects[subject_name]["teaching_guide"] = "Don't have"

                    time.sleep(random.uniform(1, 3))

                except Exception as e:
                    print("Error in scraping: ", e)

            browser.close()

        return {
            "metadata": {
                "center": f"{self.centre_name}: {self.centre}",
                "titulation": titulation,
                "year": year,
                "extraction_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "subjects": updated_subjects,
        }
