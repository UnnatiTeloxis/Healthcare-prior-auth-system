import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import FHIRValidatorPage from "./pages/FHIRValidatorPage";
import CRDSimulatorPage from "./pages/CRDSimulatorPage";
import DTRSimulatorPage from "./pages/DTRSimulatorPage";
import LoginPage from "./pages/LoginPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/fhir-validator" element={<FHIRValidatorPage />} />
        <Route path="/crd-simulator" element={<CRDSimulatorPage />} />
        <Route path="/dtr-simulator" element={<DTRSimulatorPage />} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
