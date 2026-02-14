import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
    /* Mobile-first responsive design */
    
    /* Main container styling */
    .main {
        padding-top: 1rem;
    }
    
    /* Header styling */
    h1 {
        color: #1e293b;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 0.5rem;
        font-size: clamp(1.5rem, 5vw, 2.5rem);
    }
    
    h3 {
        color: #64748b;
        font-weight: 400;
        margin-bottom: 2rem;
        font-size: clamp(1rem, 3vw, 1.25rem);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    [data-testid="stSidebar"] h2 {
        color: #1e293b;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #3b82f6;
    }
    
    /* Sidebar widgets */
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stMultiSelect label {
        font-weight: 600;
        color: #334155;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"] {
        border-radius: 0.5rem;
        border: 1px solid #cbd5e1;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"]:hover {
        border-color: #3b82f6;
    }
    
    /* Radio buttons */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.75rem;
    }
    
    [data-testid="stSidebar"] .stRadio > div > label {
        background-color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        border: 1px solid #cbd5e1;
        transition: all 0.2s ease;
    }
    
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        border-color: #3b82f6;
        background-color: #eff6ff;
    }
    
    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        background-color: #3b82f6;
        color: white;
        border-color: #3b82f6;
    }
    
    /* Multi-select styling */
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background-color: #3b82f6;
        border-radius: 0.375rem;
    }
    
    /* Download button */
    .stDownloadButton button {
        background-color: #3b82f6;
        color: white;
        border: none;
        padding: 0.625rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 600;
        transition: all 0.2s ease;
        margin-top: 1.5rem;
        width: 100%;
    }
    
    .stDownloadButton button:hover {
        background-color: #2563eb;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }
    
    /* AG Grid custom styling */
    .ag-theme-streamlit {
        border-radius: 0.75rem;
        overflow: hidden;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        width: 100%;
    }
    
    .ag-header {
        background-color: #f1f5f9;
        border-bottom: 2px solid #cbd5e1;
        font-weight: 600;
        color: #1e293b;
        font-size: clamp(0.75rem, 2vw, 0.95rem);
    }
    
    .ag-header-cell-label {
        justify-content: center;
    }
    
    .ag-row {
        border-bottom: 1px solid #f1f5f9;
    }
    
    .ag-row:hover {
        background-color: #f8fafc;
    }
    
    .ag-cell {
        line-height: 45px;
        font-size: clamp(0.75rem, 2vw, 0.95rem);
    }
    
    /* Pinned columns */
    .ag-pinned-left-header {
        border-right: 2px solid #cbd5e1 !important;
    }
    
    .ag-pinned-left-cols-container {
        border-right: 2px solid #e2e8f0 !important;
    }
    
    /* Tooltip styling */
    .ag-tooltip {
        background-color: #1e293b;
        color: white;
        border-radius: 0.375rem;
        padding: 0.5rem 0.75rem;
        font-size: 0.875rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Horizontal rule */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #e2e8f0;
    }
    
    /* Remove default Streamlit padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Custom animations */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .main > div {
        animation: fadeIn 0.5s ease;
    }
    
    /* Metrics styling for mobile */
    [data-testid="stMetricValue"] {
        font-size: clamp(1.25rem, 4vw, 1.875rem);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: clamp(0.75rem, 2vw, 0.875rem);
    }
    
    /* Mobile-specific adjustments */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        
        h1 {
            font-size: 1.5rem;
            margin-bottom: 0.25rem;
        }
        
        h3 {
            font-size: 0.95rem;
            margin-bottom: 1rem;
        }
        
        hr {
            margin: 1rem 0;
        }
        
        /* Reduce metric spacing on mobile */
        [data-testid="stMetric"] {
            padding: 0.5rem;
        }
        
        /* Make AG Grid scrollable horizontally on mobile */
        .ag-theme-streamlit {
            font-size: 0.75rem;
        }
        
        .ag-cell {
            line-height: 40px;
        }
        
        .ag-header {
            font-size: 0.75rem;
        }
        
        /* Adjust download button */
        .stDownloadButton button {
            padding: 0.5rem 1rem;
            font-size: 0.875rem;
        }
        
        /* Color legend cards */
        div[style*="padding: 10px"] {
            padding: 8px !important;
            font-size: 0.8rem !important;
        }
    }
    
    /* Tablet adjustments */
    @media (min-width: 769px) and (max-width: 1024px) {
        .block-container {
            padding-left: 1.5rem;
            padding-right: 1.5rem;
        }
        
        h1 {
            font-size: 2rem;
        }
        
        h3 {
            font-size: 1.1rem;
        }
    }
    
    /* Ensure grid is responsive */
    .stDataFrame, [data-testid="stDataFrame"] {
        width: 100%;
        overflow-x: auto;
    }
    </style>
    """, unsafe_allow_html=True)
