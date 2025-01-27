from streamlit_elements import nivo, mui, elements

import streamlit as st
import requests
import random

class Pie:
    def create_chart(self, data, height=350, unique_key="pie-chart"):
        new_data = []
        for i, j in data.items():
            color = random.randint(0, 360)
            new_data.append({"id": i, "label": i, "value": j, "color": f"hsl({color}, 70%, 50%)"})
        new_fill = []
        for i, j in data.items():
            moyou = random.choice(["dots", "lines", "squares"])
            new_fill.append({ "match": { "id": i }, "id": moyou })
        with elements(unique_key):
            with mui.Box(sx={"height": height}): # グラフの大きさ
                nivo.Pie(
                    data=new_data,
                    margin={ "top": 40, "right": 80, "bottom": 30, "left": 80 },
                    startAngle=0,
                    endAngle=360,
                    innerRadius=0.5,
                    padAngle=0.7,
                    cornerRadius=3,
                    activeOuterRadiusOffset=8,
                    borderWidth=1,
                    borderColor={
                        "from": "color",
                        "modifiers": [
                            [
                                "darker",
                                0.2,
                            ]
                        ]
                    },
                    arcLinkLabelsSkipAngle=10,
                    arcLinkLabelsTextColor="grey",
                    arcLinkLabelsThickness=2,
                    arcLinkLabelsColor={ "from": "color" },
                    arcLabelsSkipAngle=10,
                    arcLabelsTextColor={
                        "from": "color",
                        "modifiers": [
                            [
                                "darker",
                                2
                            ]
                        ]
                    },
                    defs=[
                        {
                            "id": "dots",
                            "type": "patternDots",
                            "background": "inherit",
                            "color": "rgba(255, 255, 255, 0.3)",
                            "size": 4,
                            "padding": 1,
                            "stagger": True
                        },
                        {
                            "id": "lines",
                            "type": "patternLines",
                            "background": "inherit",
                            "color": "rgba(255, 255, 255, 0.3)",
                            "rotation": -45,
                            "lineWidth": 6,
                            "spacing": 10
                        },
                        {
                            "id": 'squares',
                            "type": 'patternSquares',
                            "background": 'inherit',
                            "color": 'rgba(255, 255, 255, 0.3)',
                            "size": 6,
                            "padding": 1,
                            "stagger": True
                        },
                    ],
                    fill=new_fill,
                    key=unique_key
                )
