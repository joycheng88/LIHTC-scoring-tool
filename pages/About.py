import streamlit as st
from pathlib import Path

#######################################################################################################################################
# Page Configuration and Formatting
#######################################################################################################################################

st.set_page_config(
    page_title="About LIHTC Scoring Tool",
    layout="wide"
)

# Apply consistent styling from main app
st.markdown("""
    <style>
        /* === Global Defaults === */
        * {
            border-radius: 4px !important;
        }

        /* === Input Styling === */
        .stButton > button,
        .stTextInput > div > div,
        .stSelectbox > div,
        .stSlider > div,
        .stCheckbox > div,
        .stRadio > div,
        .stForm,
        .stDataFrame,
        .stMetric {
            border-radius: 4px !important;
        }

        /* === Info Box Styling === */
        .info-box {
            background-color: #f8f9fa;
            border-left: 4px solid #2B2D42;
            padding: 20px;
            border-radius: 4px;
            margin: 20px 0;
        }

        .highlight-box {
            background-color: #e8f4fd;
            border: 1px solid #2B2D42;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }

        .feature-card {
            background-color: #ffffff;
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* === Navigation Button Styling === */
        .nav-button {
            background-color: #2B2D42;
            color: white;
            padding: 12px 24px;
            border-radius: 4px;
            text-decoration: none;
            display: inline-block;
            margin: 10px 5px;
            font-weight: 500;
            transition: background-color 0.3s;
            text-align: center;
        }

        .nav-button:hover {
            background-color: #1a1c2e;
            color: white;
            text-decoration: none;
        }
    </style>
""", unsafe_allow_html=True)

#######################################################################################################################################
# Main Page Content
#######################################################################################################################################

st.title("About the LIHTC Scoring Tool")

# Hero section
st.markdown("""
<div class="highlight-box">
    <h3>Empowering Small Developers with Data-Driven Insights</h3>
    <p style="font-size: 18px; margin-bottom: 0;">
        A comprehensive tool designed to help smaller developers assess the feasibility 
        of obtaining Low-Income Housing Tax Credits (LIHTC) from the government.
    </p>
</div>
""", unsafe_allow_html=True)

# Main content in columns
col1, col2 = st.columns([2, 1])

with col1:
    # What is LIHTC section
    st.header("What is LIHTC?")
    
    st.markdown("""
    <div class="info-box">
        <h4>Low-Income Housing Tax Credit Program</h4>
        <p>
            The Low-Income Housing Tax Credit (LIHTC) is a federal program designed to incentivize the development and rehabilitation of affordable rental housing across the United States. Established in 1986 through the Tax Reform Act, it has become the nation's primary tool for creating affordable housing.
        </p>
        <p>
            The program provides tax credits to developers who agree to rent a certain portion of their housing units to low-income households at below-market rates for a minimum of 30 years. This program exists because the traditional real estate market often is not effective enough in creating quality rental housing for low-income individuals and families. LIHTC is helpful in bridging this housing gap by incentivizing private investment from developers to create affordable housing projects. It does this by providing a reduction in income tax liability to those who invest in affordable rental housing. 
        </p>
        <p>
            Another benefit of the program comes in the form of community revitalization, and economic growth/partnerships. By encouraging the construction of new affordable housing projects and the rehabilitation of existing units, the overall supply of affordable rental options is expanded. Furthermore, LIHTC is able to promote collaboration between federal and state governments and private developers and investors. This building of social and economic foundations addresses larger social goals by increasing disposable income for low-income households, potentially bettering access to education, improving health outcomes, and revitalizing communities overall.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Why this tool exists
    st.header("Why This Tool Exists")
    
    st.markdown("""
    ### The Challenge
    
    Smaller developers often face challenges when seeking to secure tax credits, especially for initiatives like the LIHTC, due to a litany of factors. Issues such as complexity, competition, costs, and approval act as barriers for smaller developers.
    
    These programs are complex, requiring specialized legal, accounting, and compliance expertise that can be costly and difficult for smaller organizations to access. The competitive allocation process—particularly for the oversubscribed 9% credits—is typically driven by state-managed scoring systems that tend to favor larger, experienced developers or projects that align perfectly with narrowly defined criteria. This puts smaller or community-driven projects at a disadvantage. Additionally, these developments require significant upfront investment in land acquisition, feasibility studies, design, legal work, and community engagement—all before credits are awarded. Without access to flexible pre-development financing, these early costs can be prohibitive.
    
    Even with recent improvements like transferable tax credits, smaller projects often face high transaction costs and may not generate enough tax liability to fully benefit from the credits. This, combined with the fear of audits and compliance risks, can discourage participation. Finally, local government approval or financial support is frequently required or heavily weighted in allocation decisions. This can give municipalities the power to block projects or skew development away from high-opportunity areas—further complicating efforts by smaller developers to enter the affordable housing space. Addressing these barriers is essential for creating a more equitable and inclusive tax credit system.
    
    ### The Solution
    
    This scoring tool levels the playing field by providing small developers with 
    the same analytical capabilities that large firms use to evaluate potential projects. 
    The better planned and more liveable your proposed development location, the higher 
    your competitive advantage in the LIHTC allocation process.
    """)

    # How it works
    st.header("How it works")
    
    st.markdown("""
    Location Analysis: The LIHTC scoring tool uses data collected from the different development locations in the Atlanta Area to provide comprehensive scoring for the significant factors used in determining application acceptance. Scoring for transportation is based on transportation services and their availability in reference to the proposed location. Education scoring is based on the College and Career Readiness Performance Index scores based on the appropriate year averages. Other community amenities are scored based on the criteria outlined in the State of Georgia 2024 - 2025 Qualified Allocation Plan, which can be found under the documentation tab. 
    
    Data Visualization: The tool offers interactive maps and charts for visualizing the data scoring for each location. This aspect of the tool allows potential developers to better analyze the advantages and challenges in relation to other areas on the map.       
    """)

with col2:
    # Development team info
    st.header("Development Team")
    
    st.markdown("""
    <div class="info-box">
        <h4>Emory University Students</h4>
        <p>
            This tool was developed by students at Emory University as part of an 
            initiative to support equitable housing development and provide accessible 
            technology solutions for smaller developers.
        </p>
        <p>
            <strong>Mission:</strong> Democratize access to housing development insights 
            and support the creation of affordable housing in underserved communities.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tool capabilities
    st.subheader("Tool Capabilities")
    
    capabilities = [
        "Location scoring for 4 key criteria",
        "Interactive mapping interface", 
        "Historical application analysis",
        "QAP documentation access"
    ]
    
    for capability in capabilities:
        st.markdown(f"✓ {capability}")

st.markdown("""
<div class="highlight-box">
    <h3>Ready to Get Started?</h3>
    <p>
        Use the LIHTC Scoring Tool to evaluate your potential development sites 
        and improve your competitive position in the tax credit allocation process.
    </p>
</div>
""", unsafe_allow_html=True)

# Navigation buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Start Scoring Tool", use_container_width=True):
        st.switch_page("scoring_tool.py")

with col2:
    if st.button("View QAP Documentation", use_container_width=True):
        st.switch_page("pages/QAP_Documentation.py")

with col3:
    if st.button("Scoring Criteria", use_container_width=True):
        st.switch_page("pages/QAP_Criteria.py")