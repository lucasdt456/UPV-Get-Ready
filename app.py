import json

import pandas as pd
import streamlit as st
from src.upv_scraper_project import constants
from src.upv_scraper_project.ia_planner import generate_markdown_resume
from src.upv_scraper_project.scraper import UPVScraper

st.set_page_config(
    page_title="UPV Get Ready",
    page_icon="🎓",
    menu_items={
        "About": """
        # UPV Get Ready
        
        This is website to help you prepare for the UPV's degrees programmes.

        - **Author:** Lucas
        - **Version:** 1.0
        """,
        "Get Help": "https://github.com/lucasdt456",
        "Report a bug": "mailto:virgillitolucas430@gmail.com",
    },
)


def init_session_state():
    default_states = {
        "presentation": False,
        "current_center": None,
        "titulations": {},
        "titulation": None,
        "years": {},
        "year": None,
        "subjects": {},
        "presentate_data": pd.DataFrame(),
        "save_all_contents": {},
        "json_str": "",
        "json_ready": False,
        "md_resume": None,
    }

    for key, state in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = state


def reset_state_app():
    st.session_state.current_center = None
    st.session_state.titulations = {}
    st.session_state.titulation = None
    st.session_state.years = {}
    st.session_state.year = None
    st.session_state.subjects = {}
    st.session_state.presentate_data = pd.DataFrame()
    st.session_state.save_all_contents = {}
    st.session_state.json_str = ""
    st.session_state.json_ready = False
    st.session_state.md_resume = None


def generate_df(
    center: str, titulation: str, year: str, subjects: dict
) -> pd.DataFrame:

    data_rows = []

    for name, details in subjects.items():
        data_rows.append(
            {
                "Centre": center,
                "Titulation": titulation,
                "Year of course": year,
                "Subject": name,
                "Code": details.get("code", ""),
                "Character": details.get("character", ""),
                "Semester": details.get("semester", ""),
                "Credits": details.get("credits", ""),
            }
        )

    df = pd.DataFrame(data_rows)
    return df


def render_initial_view():
    if not st.session_state.presentation:
        st.toast(
            "Welcome to **UPV Get Ready**: the app to help you prepare for your upcoming academic year at the UPV.",
            icon="✨",
            duration=10,
        )
        st.session_state.presentation = True

    st.markdown(
        """
            <h1 style="color: #e5554f; text-align: center;">🏫 UPV - Prepare for the Course</h1>
            """,
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='border: 1px solid #e5554f;'>", unsafe_allow_html=True)

    if st.session_state.presentate_data.empty:
        centre_idx = (
            constants.CENTRES_LIST.index(st.session_state.current_center)
            if st.session_state.current_center in constants.CENTRES_LIST
            else None
        )

        st.header("Select centre")
        centre = st.selectbox(
            label="All centres:",
            options=constants.CENTRES_LIST,
            placeholder="Select centre",
            index=centre_idx,
            disabled=st.session_state.current_center is not None,
        )

        if centre:
            st.success(f"✅ You have selected the centre: **{centre}**")
            _, middle, _ = st.columns(3)

            if middle.button(
                "**Search all titulations 🚀🎓**",
                use_container_width=True,
                disabled=st.session_state.current_center is not None,
                key="titulation_button",
            ):
                with st.spinner(f"Search all titulations of: *{centre}*..."):
                    scraper = UPVScraper(centre)
                    st.session_state.titulations = scraper.obtain_titulation()
                    st.session_state.current_center = centre
                    st.rerun()

        if st.session_state.titulations:
            st.header("Select titulation")

            tit_list = list(st.session_state.titulations)
            tit_idx = (
                tit_list.index(st.session_state.titulation)
                if st.session_state.titulation in tit_list
                else None
            )

            st.session_state.titulation = st.selectbox(
                label=f"All titulations of {centre}:",
                options=list(st.session_state.titulations.keys()),
                placeholder="Select titulation",
                index=tit_idx,
                disabled=bool(st.session_state.years),
            )
            if st.session_state.titulation:
                st.success(
                    f"✅ You have selected the titulation: **{st.session_state.titulation}**"
                )
                _, middle, _ = st.columns(3)

                if middle.button(
                    "**Search all courses (years) 🚀🧑‍🎓**",
                    use_container_width=True,
                    disabled=bool(st.session_state.years),
                    key="year_button",
                ):
                    with st.spinner(
                        f"Search all years of: *{st.session_state.current_center}* - *{st.session_state.titulation}*..."
                    ):
                        scraper = UPVScraper(centre)
                        target_url = st.session_state.titulations[
                            st.session_state.titulation
                        ]
                        st.session_state.years = scraper.obtain_course(target_url)
                        st.rerun()

        if st.session_state.years:
            st.header("Select year")

            year_list = list(st.session_state.years)
            year_idx = (
                year_list.index(st.session_state.year)
                if st.session_state.year in st.session_state.years
                else None
            )

            year = st.selectbox(
                label=f"All years of {st.session_state.titulation}:",
                options=list(st.session_state.years.keys()),
                placeholder="Select year",
                index=year_idx,
                disabled=bool(st.session_state.subjects),
            )
            st.warning(
                "If you choose: *'Asignaturas Alfabéticamente'* all the courses on your degree programme will be displayed\n**¡Not recommended!**",
                icon="⚠️",
            )

            if year:
                st.success(f"✅ You have selected the year: **{year}**")

                _, middle, _ = st.columns(3)

                if middle.button(
                    "Search all subjects 🚀📚",
                    use_container_width=True,
                    disabled=bool(st.session_state.subjects),
                    key="subjects_button",
                ):
                    st.session_state.year = year
                    with st.spinner(
                        f"Search all subjects of: *{st.session_state.current_center}* - *{st.session_state.titulation}* - *{st.session_state.year}*..."
                    ):
                        scraper = UPVScraper(centre)
                        target_url = st.session_state.years[st.session_state.year]
                        st.session_state.subjects = scraper.extract_subjects(target_url)
                        st.session_state.presentate_data = generate_df(
                            st.session_state.current_center,
                            st.session_state.titulation,
                            st.session_state.year,
                            st.session_state.subjects,
                        )
                        st.rerun()
    else:
        with st.expander("🗂️ View All data extracted", expanded=False):
            st.markdown(
                f"""
**Centre:**
- {st.session_state.current_center}

**Titulation:** 
- {st.session_state.titulation}

**Year:** 
- {st.session_state.year}

**Subjects:**
{"\n".join(f"- {sub}" for sub in st.session_state.subjects)}
                    """
            )
        st.success(
            "✅ Subjects extracted! Go to 'Table' in the sidebar to view them and obtain all the studie planification."
        )
        _, middle, _ = st.columns([1, 2, 1])

        if middle.button(
            "Start Over / Choose another degree",
            icon="🔃",
            use_container_width=True,
        ):
            reset_state_app()
            st.rerun()


def render_table_view():
    if not st.session_state.presentate_data.empty:
        st.markdown(
            """<h2 style="color: #e5554f; text-align: center; font-weight: bold;">🗂️ All data extracted:</h2>""",
            unsafe_allow_html=True,
        )
        st.markdown("<hr style='border: 1px solid #e5554f;'>", unsafe_allow_html=True)

        if not st.session_state.json_ready:
            st.dataframe(
                st.session_state.presentate_data,
                hide_index=True,
                use_container_width=True,
                placeholder=f"Resume of your selection: {st.session_state.current_center} - {st.session_state.titulation} - {st.session_state.year}",
            )

            left, middle, right = st.columns([1, 2, 1])
            if middle.button(
                "Extract Teaching Guides ⚙️",
                type="primary",
                use_container_width=True,
                disabled=bool(st.session_state.save_all_contents),
            ):
                with st.spinner(
                    "Extracting all guide... This may take a few minutes. Pleas wait... ⌛"
                ):
                    scraper = UPVScraper(st.session_state.current_center)

                    export_payload = scraper.extract_subjects_teaching_guide(
                        subjects=st.session_state.subjects,
                        titulation=st.session_state.titulation,
                        year=st.session_state.year,
                    )
                    st.session_state.save_all_contents = export_payload
                    st.session_state.json_str = json.dumps(
                        export_payload, ensure_ascii=False, indent=4
                    )
                    st.session_state.json_ready = True
                    st.balloons()
                    st.rerun()

        else:
            st.success("✅ JSON generated successfully! Download all now.")

            left, right = st.columns(2)

            left.download_button(
                label="Download JSON",
                data=st.session_state.json_str,
                file_name="upv_data_study.json",
                use_container_width=True,
                mime="application/json",
                icon="📥",
            )

            if right.button(
                "Scheduler by LLM",
                use_container_width=True,
                icon="🧠",
            ):
                with st.spinner(
                    "Generate the Summary by the LLM (this may take a few minutes)...",
                ):
                    st.session_state.md_resume = generate_markdown_resume(
                        st.session_state.json_str
                    )

            if st.session_state.md_resume:
                with st.expander("View all summary", icon="📑"):
                    st.markdown(st.session_state.md_resume)

                _, middle, _ = st.columns(3)
                middle.download_button(
                    label="Download AI Summary (.md)",
                    data=st.session_state.md_resume,
                    file_name="upv_study_plan.md",
                    use_container_width=True,
                    mime="text/markdown",
                    icon="📥",
                )

    else:
        st.markdown(
            """<h2 style="color: lightblue; text-align: center;">Without Data to Prepare te next course</h2>""",
            unsafe_allow_html=True,
        )
        st.markdown("<hr style='border: 1px solid lightblue;'>", unsafe_allow_html=True)
        st.info(
            "You don't have the data to prepare the future course. Go to 'Initial' in the sidebar.",
            icon="❌",
        )


def main():
    init_session_state()

    st.sidebar.header("Navigation")
    section = st.sidebar.radio(label="Go to:", options=["Initial", "Table"])

    if section == "Initial":
        render_initial_view()
    elif section == "Table":
        render_table_view()


if __name__ == "__main__":
    main()
