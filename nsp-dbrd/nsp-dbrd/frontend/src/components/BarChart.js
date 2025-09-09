import React, { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import axios from 'axios';

const BarChart = () => {
    const [chartData, setChartData] = useState({});
    
    const fetchData = async () => {
        try {
            const response = await axios.get('/api/top-states');
            const data = response.data;

            const states = data.map(item => item.state);
            const applications = data.map(item => item.applications);

            setChartData({
                labels: states,
                datasets: [
                    {
                        label: 'Number of Applications',
                        data: applications,
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                    },
                ],
            });
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    return (
        <div>
            <h2>Applications by State</h2>
            <Bar data={chartData} options={{ responsive: true }} />
        </div>
    );
};

export default BarChart;