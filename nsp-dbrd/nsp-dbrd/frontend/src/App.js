import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import BarChart from './components/BarChart';
import PieChart from './components/PieChart';
import SummaryCard from './components/SummaryCard';
import api from './services/api';

function App() {
    const [summaryData, setSummaryData] = useState({});
    const [barChartData, setBarChartData] = useState([]);
    const [pieChartData, setPieChartData] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const summaryResponse = await api.get('/api/summary');
                setSummaryData(summaryResponse.data);

                const barChartResponse = await api.get('/api/top-schemes-payments');
                setBarChartData(barChartResponse.data);

                const pieChartResponse = await api.get('/api/gender-distribution');
                setPieChartData(pieChartResponse.data);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };

        fetchData();
    }, []);

    return (
        <Router>
            <div className="App">
                <h1>NSP Dashboard</h1>
                <SummaryCard data={summaryData} />
                <Switch>
                    <Route path="/bar-chart">
                        <BarChart data={barChartData} />
                    </Route>
                    <Route path="/pie-chart">
                        <PieChart data={pieChartData} />
                    </Route>
                    <Route path="/">
                        <h2>Welcome to the NSP Dashboard</h2>
                    </Route>
                </Switch>
            </div>
        </Router>
    );
}

export default App;