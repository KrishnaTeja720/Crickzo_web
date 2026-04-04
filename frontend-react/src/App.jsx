import React, { useContext } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthContext } from './context/AuthContext';
import Layout from './components/Layout';

import Splash from './screens/Splash';
import Login from './screens/Login';
import SignUp from './screens/SignUp';
import ForgotPassword from './screens/ForgotPassword';
import VerifyOTP from './screens/VerifyOTP';
import ResetPassword from './screens/ResetPassword';
import Home from './screens/Home';
import Profile from './screens/Profile';
import CreateMatch from './screens/CreateMatch';
import SetupMatch from './screens/SetupMatch';
import Scoring from './screens/Scoring';
import Predictions from './screens/Predictions';
import MyMatches from './screens/MyMatches';
import Scorecard from './screens/Scorecard';

function App() {
  const { user } = useContext(AuthContext);

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to={user ? "/home" : "/splash"} replace />} />
        <Route path="/splash" element={<Splash />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/forgot_password" element={<ForgotPassword />} />
        <Route path="/verify_otp" element={<VerifyOTP />} />
        <Route path="/reset_password" element={<ResetPassword />} />
        
        <Route path="/home" element={<Home />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/create_match" element={<CreateMatch />} />
        <Route path="/setup_match/:matchId" element={<SetupMatch />} />
        <Route path="/scoring/:matchId" element={<Scoring />} />
        <Route path="/scoring" element={<Navigate to="/home" replace />} />
        <Route path="/predictions" element={<Predictions />} />
        <Route path="/my_matches" element={<MyMatches />} />
        <Route path="/scorecard/:matchId" element={<Scorecard />} />
        
        {/* Add more routes as we build the screens */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}

export default App;
