import React, { useEffect, useState } from 'react';
import { fetchSummaryData } from '../services/api';

const SummaryCard = () => {
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const getSummaryData = async () => {
            try {
                const data = await fetchSummaryData();
                setSummary(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        getSummaryData();
    }, []);

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div className="summary-card">
            <h2>Summary</h2>
            <p>Total Applications: {summary.total_applications}</p>
            <p>Total Funding: {summary.total_funding}</p>
            <p>Average Payment: {summary.avg_payment}</p>
        </div>
    );
};

export default SummaryCard;