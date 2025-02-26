import React, { useState } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import TaskExecution from './components/TaskExecution';

function App() {
  const [selectedSection, setSelectedSection] = useState('home');

  const handleSectionSelect = (section: string) => {
    setSelectedSection(section);
  };

  return (
    <div className="App">
      <Sidebar 
        selectedSection={selectedSection}
        onSectionSelect={handleSectionSelect}
      />
      <div className="main-content">
        <TaskExecution />
      </div>
    </div>
  );
}

export default App;
