import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api'; // Adjust the base URL as needed

export const fetchTopStates = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/top-states`);
        return response.data;
    } catch (error) {
        console.error('Error fetching top states:', error);
        throw error;
    }
};

export const fetchGenderDistribution = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/gender-distribution`);
        return response.data;
    } catch (error) {
        console.error('Error fetching gender distribution:', error);
        throw error;
    }
};

export const fetchCategories = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/categories`);
        return response.data;
    } catch (error) {
        console.error('Error fetching categories:', error);
        throw error;
    }
};

export const fetchFundingBreakdown = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/funding-breakdown`);
        return response.data;
    } catch (error) {
        console.error('Error fetching funding breakdown:', error);
        throw error;
    }
};

export const fetchIncomeDistribution = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/income-distribution`);
        return response.data;
    } catch (error) {
        console.error('Error fetching income distribution:', error);
        throw error;
    }
};

export const fetchTopDistrictsPayments = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/top-districts-payments`);
        return response.data;
    } catch (error) {
        console.error('Error fetching top districts payments:', error);
        throw error;
    }
};

export const fetchTopSchemesPayments = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/top-schemes-payments`);
        return response.data;
    } catch (error) {
        console.error('Error fetching top schemes payments:', error);
        throw error;
    }
};

export const fetchCategoryPayments = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/category-payments`);
        return response.data;
    } catch (error) {
        console.error('Error fetching category payments:', error);
        throw error;
    }
};

export const fetchGenderPayments = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/gender-payments`);
        return response.data;
    } catch (error) {
        console.error('Error fetching gender payments:', error);
        throw error;
    }
};

export const fetchTopSchemesApplications = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/top-schemes-applications`);
        return response.data;
    } catch (error) {
        console.error('Error fetching top schemes applications:', error);
        throw error;
    }
};

export const fetchSummary = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/summary`);
        return response.data;
    } catch (error) {
        console.error('Error fetching summary:', error);
        throw error;
    }
};