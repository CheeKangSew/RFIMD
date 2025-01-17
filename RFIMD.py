import streamlit as st
import pandas as pd
import numpy as np

def calculate_imd_frequencies(f1, f2, n_max, m_max):
    frequencies = []
    for n in range(n_max + 1):
        for m in range(m_max + 1):
            if n == 0 and m == 0:
                continue  # Skip the (0, 0) combination
            for sign1 in [1, -1]:
                for sign2 in [1, -1]:
                    f_out = abs(sign1 * n * f1 + sign2 * m * f2)
                    frequencies.append((n, m, sign1, sign2, f_out))
    return frequencies

def check_frequency_overlap(frequencies, ranges):
    overlaps = []
    for freq_data in frequencies:
        n, m, sign1, sign2, f_out = freq_data
        overlap_info = []
        for range_name, (low, high) in ranges.items():
            if low <= f_out <= high:
                overlap_info.append(range_name)
        overlaps.append((n, m, sign1, sign2, f_out, ", ".join(overlap_info)))
    return overlaps

def main():
    st.title("RF Intermodulation Distortion (IMD) Frequency Calculator")

    # Sidebar inputs
    with st.sidebar:
        st.header("Input Parameters")
        f1 = st.number_input("LMR Tx Freq in MHz:", min_value=0.0, value=100.0, step=0.1)
        f2 = st.number_input("WiFi Tx Freq in MHz:", min_value=0.0, value=200.0, step=0.1)
        st.write("**Note:** Simultaneous LMR Tx & WiFi Tx operation")

    if f2 <= f1:
        st.error("F2 must be greater than F1. Please adjust the inputs.")
        return

    # Define harmonic ranges
    n_max, m_max = 5, 5

    # Frequency ranges for reference
    frequency_ranges = {
        "GNSS L1, E1, B1": (1559, 1610),
        "GNSS L2, E6, B3, L6": (1215, 1300),
        "GNSS L5, E5, B2, L3": (1164, 1215),
        "WLAN 2.4G band": (2400, 2500),
        "WLAN 5G band": (5725, 5875),
        "WLAN 6G band": (5945, 7125),
        "LMR UHF": (350, 470),
        "LMR 800": (806, 870),
    }

    # Display all frequency ranges as reference
    st.subheader("Frequency Ranges for Reference")
    freq_range_df = pd.DataFrame(
        [(name, f"{low} MHz - {high} MHz") for name, (low, high) in frequency_ranges.items()],
        columns=["Frequency Band", "Range"]
    )
    st.table(freq_range_df)

    # Only GNSS ranges are used for overlap checking
    gnss_ranges = {
        "GNSS L1, E1, B1": (1559, 1610),
        "GNSS L2, E6, B3, L6": (1215, 1300),
        "GNSS L5, E5, B2, L3": (1164, 1215),
    }

    if st.button("Calculate IMD Frequencies"):
        # Calculate IMD frequencies
        raw_frequencies = calculate_imd_frequencies(f1, f2, n_max, m_max)

        # Check for overlaps with GNSS ranges
        frequencies_with_overlap = check_frequency_overlap(raw_frequencies, gnss_ranges)

        # Convert results to DataFrame
        df = pd.DataFrame(frequencies_with_overlap, columns=[
            "n", "m", "Sign of n", "Sign of m", "IMD Frequency (MHz)", "Overlap"
        ])

        df = df.sort_values(by="IMD Frequency (MHz)").reset_index(drop=True)

        # Highlight overlaps in the table
        def highlight_overlap(row):
            if row["Overlap"]:
                return ["background-color: yellow"] * len(row)
            return [""] * len(row)

        st.subheader("Calculated IMD Frequencies")
        st.dataframe(df.style.apply(highlight_overlap, axis=1))

        # Provide download option
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name="imd_frequencies_with_gnss_overlap.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
