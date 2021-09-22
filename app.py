import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json


@st.cache(allow_output_mutation=True)
def load_data(file):
    with open(file) as input_file:
        data = json.load(input_file)
    df = pd.json_normalize(data['stations'])
    return df


def well_trajectory(df):
    fig = go.Figure(data=go.Scatter3d(
        x=df["easting"], y=df["northing"], z=df["tvd"],
        marker=dict(
            size=4,
            color=df["vertical_section"],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Vertical Section')
        ),
        hovertemplate='<extra></extra><br>' + '<b>North (ft)</b>: %{y:.2f}<br>' +
                      '<b>East (ft)</b>: %{x:.2f}<br>' + '<b>TVD (ft)</b>: %{z:.2f}<br>',
        line=dict(
            color='darkblue',
            width=2
        )
    ))
    fig.update_layout(scene=dict(
        xaxis=dict(
            backgroundcolor="rgb(200, 200, 230)",
            title="East (ft)",
            gridcolor="white",
            showbackground=True,
            zerolinecolor="white", ),
        yaxis=dict(
            backgroundcolor="rgb(230, 200,230)",
            title="North (ft)",
            gridcolor="white",
            showbackground=True,
            zerolinecolor="white"),
        zaxis=dict(
            backgroundcolor="rgb(230, 230,200)",
            title="TVD (ft)",
            gridcolor="white",
            showbackground=True,
            zerolinecolor="white", ), ),

        width=900,
        height=1000,
        margin=dict(
            r=10, l=10,
            b=10, t=10)
    )
    fig.update_scenes(zaxis_autorange="reversed")
    return st.plotly_chart(fig)


def plot_1(df):
    fig = go.Figure(data=go.Scatter(x=df["easting"], y=df["northing"], mode='markers',
                                    marker=dict(color='MediumPurple', size=10,
                                                line=dict(color='White', width=0.5)),
                                    ))
    fig.update_layout(
        xaxis=dict(ticks="outside",
                   mirror=True,
                   showline=True,
                   side='top',
                   title='East (ft)',
                   linewidth=0.5,
                   linecolor='White',
                   gridcolor='White',
                   zerolinecolor='White',
                   zerolinewidth=0.5),
        yaxis=dict(ticks="outside",
                   mirror=True,
                   showline=True,
                   side='right',
                   title='North (ft)',
                   linewidth=0.5,
                   linecolor='White',
                   gridcolor='White',
                   zerolinecolor='White',
                   zerolinewidth=0.5),
        template='plotly_dark',
        width=800,
        height=500,
        margin=dict(r=10, l=10, b=30, t=30))
    return st.plotly_chart(fig)


def plot_2(df):
    fig = go.Figure(data=go.Scatter(x=df["vertical_section"], y=df["tvd"], mode='markers',
                                    marker=dict(color='MediumPurple', size=10,
                                                line=dict(color='White', width=0.5)),
                                    ))
    fig['layout']['yaxis']['autorange'] = "reversed"
    fig.update_layout(
        xaxis=dict(ticks="outside",
                   mirror=True,
                   showline=True,
                   title='Vertical Section (ft)',
                   linewidth=0.5,
                   linecolor='White',
                   gridcolor='White',
                   zerolinecolor='White',
                   zerolinewidth=0.5),
        yaxis=dict(ticks="outside",
                   mirror=True,
                   showline=True,
                   title='TVD (ft)',
                   linewidth=0.5,
                   linecolor='White',
                   gridcolor='White',
                   zerolinecolor='White',
                   zerolinewidth=0.5),
        template='plotly_dark',
        width=800,
        height=500,
        margin=dict(r=10, l=10, b=30, t=30))
    return st.plotly_chart(fig)


def minimum_curvature(df):
    # Calculate the dogleg
    dogleg = 2 * np.arcsin(
        np.sqrt((np.sin((df['inclination'] - df['inclination_prev']) / 2)) ** 2 + np.sin(df['inclination']) *
                np.sin(df['inclination_prev']) * (np.sin((df['azimuth'] - df['azimuth_prev']) / 2)) ** 2))

    # If length is zero, prevent divison by zero.
    if df['md_diff'] == 0:
        return None, None, None, None

    # Calculate the dogleg severity in (°/100ft)
    dogleg_severity = np.rad2deg(dogleg * (100 / df['md_diff']))

    # Calculate ratio factor.  If there's no dogleg, calculate with balanced tangential instead of minimum curvature.
    if dogleg != 0.0:
        ratio_factor = 2 * np.tan(dogleg / 2) / dogleg  # minimum curvature
    else:
        ratio_factor = 1  # balanced tangential

    # Calculation for TVD depth difference between first and second survey stations
    tvd_difference = (0.5 * df['md_diff'] * (
        np.cos(df['inclination_prev']) + np.cos(df['inclination'])) * ratio_factor)

    # Calculation for northing difference between first and second survey stations
    northing_difference = 0.5 * df['md_diff'] * (
        np.sin(df['inclination_prev']) * np.cos(df['azimuth_prev']) +
        np.sin(df['inclination']) * np.cos(df['azimuth'])) * ratio_factor

    # Calculation for easting difference between first and second survey stations
    easting_difference = 0.5 * df['md_diff'] * (
        np.sin(df['inclination_prev']) * np.sin(df['azimuth_prev']) +
        np.sin(df['inclination']) * np.sin(df['azimuth'])) * ratio_factor

    return pd.Series([tvd_difference, northing_difference, easting_difference, dogleg_severity])

def average_angle(df):
    tvd_difference = df['md_diff'] * (np.cos((df['inclination_prev']+df['inclination'])/2))

    # Calculation for northing difference between first and second survey stations
    northing_difference = df['md_diff'] * (
            np.sin((df['inclination_prev']+df['inclination'])/2)) * np.cos((df['azimuth_prev']+df['azimuth'])/2)

    # Calculation for easting difference between first and second survey stations
    easting_difference = df['md_diff'] * (
            np.sin((df['inclination_prev']+df['inclination'])/2)) * np.sin((df['azimuth_prev']+df['azimuth'])/2)
    return pd.Series([tvd_difference, northing_difference, easting_difference])

def vertical_section(df):
    # Calculation for closure distance
    closure_distance = np.sqrt((df['northing'] ** 2 + df['easting'] ** 2))

    # Calculation for closure azimuth
    if df['northing'] == 0:
        closure_azimuth = 0
    else:
        closure_azimuth = np.rad2deg(np.arctan(df['easting'] / df['northing']))

    # Calculation for vertical section
    vertical_section = np.abs(closure_distance * (np.cos(
        np.deg2rad(df['vertical_azimuth'] - closure_azimuth))))

    return pd.Series(vertical_section)

def convert_df(df):
    return df.to_csv().encode('utf-8')


def main():
    html_temp = """
    <div style="background-color:tomato;padding:10px">
    <h2 style="color:white;text-align:center;">Well Trajectory App</h2>
    </div>
    """
    st.markdown(html_temp, unsafe_allow_html=True)
    st.write(" ")
    st.markdown(
        "This application is a web app used to generate oil & gas well trajectory based on different methods."
    )
    st.write(" ")
    json_file = st.file_uploader("Upload File", type=["json"])
    if json_file:
        data = json.load(json_file)
        df = pd.json_normalize(data['stations'])
        df_azi = pd.json_normalize(data)['vertical_section_azimuth']
        st.write("## Well Trajectory Dashboard")
        method = ["Default (MCM)", "AAM"]
        choice = st.sidebar.selectbox("Method", method)
        if choice == "Default (MCM)":
            button = st.button("Process")
            if button:
                df['md_diff'] = df['measured_depth'].diff(periods=1)
                df['inclination'] = df['inclination'].apply(lambda x: np.deg2rad(x))
                df['azimuth'] = df['azimuth'].apply(lambda x: np.deg2rad(x))
                df['inclination_prev'] = df['inclination'].shift(1)
                df['azimuth_prev'] = df['azimuth'].shift(1)
                df[['tvd_difference', 'northing_difference', 'easting_difference', 'dogleg_severity']] = df.apply(minimum_curvature, axis=1)
                df.fillna(0, inplace=True)
                df[['tvd','northing','easting']] = df[['tvd_difference', 'northing_difference', 'easting_difference']].cumsum()
                df['vertical_azimuth'] = float(df_azi)
                df[['vertical_section']] = df.apply(vertical_section, axis=1)
                df = df[['measured_depth','tvd','northing','easting','dogleg_severity','vertical_section']]
                well_trajectory(df)
                st.write("")
                plot_1(df)
                plot_2(df)
                csv = convert_df(df)
                st.download_button(
                    "Press to Download",
                    csv,
                    "trajectory.csv")
        elif choice == "AAM":
            button = st.button("Process")
            if button:
                df['md_diff'] = df['measured_depth'].diff(periods=1)
                df['inclination'] = df['inclination'].apply(lambda x: np.deg2rad(x))
                df['azimuth'] = df['azimuth'].apply(lambda x: np.deg2rad(x))
                df['inclination_prev'] = df['inclination'].shift(1)
                df['azimuth_prev'] = df['azimuth'].shift(1)
                df[['tvd_difference', 'northing_difference', 'easting_difference']] = df.apply(
                        average_angle, axis=1)
                df.fillna(0, inplace=True)
                df[['tvd', 'northing', 'easting']] = df[
                        ['tvd_difference', 'northing_difference', 'easting_difference']].cumsum()
                df['vertical_azimuth'] = float(df_azi)
                df[['vertical_section']] = df.apply(vertical_section, axis=1)
                df = df[['measured_depth','tvd', 'northing', 'easting', 'vertical_section']]
                well_trajectory(df)
                st.write("")
                plot_1(df)
                plot_2(df)
                csv = convert_df(df)
                st.download_button(
                        "Press to Download",
                        csv,
                        "trajectory.csv")

    else:
        print("Input a JSON file")

if __name__ == "__main__":
    main()
