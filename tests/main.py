from upv_scraper_project import constants
from upv_scraper_project.scraper import UPVScraper


def main():
    print("----- ALL CENTRES: -----")
    for centre in constants.CENTRES_LIST:
        print(f"- {centre}")
    centre = str(input("Choose a center: "))

    first_prube_scraping = UPVScraper(
        centre=centre,
    )
    print(f"Searching titulations to: {centre}...")

    first_prube_scraping.obtain_titulation()
    titulations = first_prube_scraping.titulations
    print(titulations)

    if not titulations:
        print(f"The centre '{centre}' doesn't have titulations")
        return

    print("----- ALL TITULATIONS: -----")
    for titulation in list(titulations.keys()):
        print(f"- {titulation}")

    titulation = str(input("Choose a titulation: "))

    first_prube_scraping.obtain_course(titulations[titulation])
    years = first_prube_scraping.years
    print(years)

    print(f"Searching all years to: {titulation}...")

    print("----- ALL YEARS: -----")
    for year in list(years.keys()):
        print(f"- {year}")
    print(
        "If you choose: 'Asignaturas Alfabéticamente' all the courses on your degree programme will be displayed\n¡Not recommended!"
    )
    year = str(input("Choose a year: "))

    first_prube_scraping.extract_subjects(years[year])
    first_prube_scraping.extract_subjects_teaching_guide()

    first_prube_scraping.save_all_contents(
        titulation,
        year,
    )

    first_prube_scraping.save_subject_in_json()


if __name__ == "__main__":
    main()
