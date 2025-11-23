import { Line } from "react-chartjs-2";
import { useEffect, useState } from "react";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
} from "chart.js";

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

export default function VibrationChart() {
    const [timestamps, setTimestamps] = useState([]);
    const [vibrationData, setVibrationData] = useState([]);

    // Fetch live vibration every 2 seconds
    useEffect(() => {
        const interval = setInterval(async () => {
            try {
                const res = await fetch("http://127.0.0.1:8000/sensor/data");
                const data = await res.json();

                const vibration = data?.vibration ?? 0;
                const time = new Date().toLocaleTimeString();

                setTimestamps((prev) => [...prev.slice(-20), time]);
                setVibrationData((prev) => [...prev.slice(-20), vibration]);

            } catch (err) {
                console.error("Error fetching vibration data:", err);
            }
        }, 2000);

        return () => clearInterval(interval);
    }, []);

    const chartData = {
        labels: timestamps,
        datasets: [
            {
                label: "Vibration (Hz)",
                data: vibrationData,
                borderColor: "rgb(75, 192, 192)",
                borderWidth: 2,
                fill: false,
                tension: 0.3,
                pointRadius: 0,
            },
        ],
    };

    const options = {
        responsive: true,
        scales: {
            y: {
                title: { display: true, text: "Vibration (Hz)" },
            },
            x: {
                title: { display: true, text: "Time" },
            },
        },
    };

    return (
        <div style={{ height: "300px" }}>
            <Line data={chartData} options={options} />
        </div>
    );
}
