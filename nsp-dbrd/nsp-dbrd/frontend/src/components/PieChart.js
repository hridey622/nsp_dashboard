import React, { useEffect, useState } from 'react';
import { Pie } from 'react-chartjs-2';
import api from '../services/api';

const PieChart = () => {
    const [chartData, setChartData] = useState({});
    
    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get('/api/categories');
                const categories = response.data;
                
                const data = {
                    labels: categories.map(category => category.category),
                    datasets: [{
                        data: categories.map(category => category.applications),
                        backgroundColor: [
                            '#FF6384',
                            '#36A2EB',
                            '#FFCE56',
                            '#4BC0C0',
                            '#9966FF',
                            '#FF9F40',
                        ],
                    }],
                };
                
                setChartData(data);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };

        fetchData();
    }, []);

    return (
        <div>
            <h2>Applications by Category</h2>
            <Pie data={chartData} />
        </div>
    );
};

export default PieChart;