import React, { useEffect, useRef } from "react";
import Chart from "chart.js";


export default function LineChart(props) {
  const chartRef = useRef(null);

  function processItemPrices(prices) {
    const labels = prices.map(price => price.date);
    const values = prices.map(price => price.value);

    return { 'labels': labels, 'values': values };
  }

  useEffect(() => {
    const prices = processItemPrices(props.data);
    console.log(prices);

    const config = {
      type: 'line',
      data: {
        labels: prices.labels,
        datasets: [
          {
            label: 'Price',
            backgroundColor: "#4c51bf",
            borderColor: "#4c51bf",
            data: prices.values,
            fill: false
          },
        ]
      },
      options: {
        legend: {
          display: false,
        },
        tooltips: {
          mode: "index",
          intersect: false
        },

        hover: {
          mode: "nearest",
          intersect: true
        },
        scales: {
          xAxes: [
            {
              ticks: {
                fontColor: "rgba(128,128,128,.7)"
              },
              display: true,
              gridLines: {
                display: false,
                borderDash: [2],
                borderDashOffset: [2],
                color: "rgba(33, 37, 41, 0.3)",
                zeroLineColor: "rgba(0, 0, 0, 0)",
                zeroLineBorderDash: [2],
                zeroLineBorderDashOffset: [2]
              }
            }
          ],
          yAxes: [
            {
              ticks: {
                fontColor: "rgba(128,128,128,.7)"
              },
              display: true,
              gridLines: {
                display: true,
                borderDash: [3],
                borderDashOffset: [3],
                drawBorder: false,
                color: "rgba(33, 37, 41, 0.3)",
                zeroLineColor: "rgba(33, 37, 41, 0)",
                zeroLineBorderDash: [2],
                zeroLineBorderDashOffset: [2]
              }
            }
          ]
        }
      }
    };
    
    new Chart(chartRef.current, config);

  }, [props.data]);

  return (
    <div className="relative py-4 pr-2">
      <canvas ref={chartRef} id="line-chart"></canvas>
    </div>
  );
}
