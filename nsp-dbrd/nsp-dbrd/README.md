# NSP Dashboard Project

## Overview
The NSP Dashboard project is a web application that provides insights and visualizations based on data from the NSP (National Service Program). The application is structured into a backend and a frontend, utilizing Flask for the backend API and React for the frontend user interface.

## Project Structure
```
nsp-dbrd
├── backend
│   ├── app
│   │   ├── __init__.py          # Initializes the Flask application
│   │   ├── config.py            # Configuration settings for the Flask app
│   │   ├── database.py          # Handles database connections and queries
│   │   └── routes.py            # Defines API routes for the application
│   ├── run.py                   # Entry point for running the backend application
│   └── requirements.txt         # Python dependencies for the backend
├── frontend
│   ├── public
│   │   └── index.html           # Main HTML file for the frontend application
│   ├── src
│   │   ├── components
│   │   │   ├── BarChart.js      # Component for rendering bar charts
│   │   │   ├── PieChart.js      # Component for rendering pie charts
│   │   │   └── SummaryCard.js    # Component for displaying summary information
│   │   ├── services
│   │   │   └── api.js           # Functions for making API calls to the backend
│   │   ├── App.js               # Main React component for the application
│   │   └── index.js             # Entry point for the React application
│   └── package.json             # Configuration file for npm
└── README.md                    # Documentation for the project
```

## Setup Instructions

### Backend
1. Navigate to the `backend` directory.
2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the backend application:
   ```
   python run.py
   ```

### Frontend
1. Navigate to the `frontend` directory.
2. Install the required npm packages:
   ```
   npm install
   ```
3. Start the frontend application:
   ```
   npm start
   ```

## Usage
- Access the backend API at `http://localhost:5000/api/`.
- The frontend application will be available at `http://localhost:3000/`.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License.