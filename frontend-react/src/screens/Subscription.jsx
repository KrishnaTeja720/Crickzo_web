import React from 'react';
import { useNavigate } from 'react-router-dom';

const Subscription = () => {
    const navigate = useNavigate();

    const features = [
        {
            title: "Ad-Free Experience",
            description: "Pure learning and scoring, no interruptions.",
            icon: "⚡"
        },
        {
            title: "Exclusive Tools",
            description: "Advanced analytics, insights, and premium features.",
            icon: "💎"
        },
        {
            title: "Advanced Analytics",
            description: "Deep dive into your performance with detailed stats.",
            icon: "📊"
        }
    ];

    const plans = [
        {
            name: "Monthly",
            price: "$9.99",
            period: "/month",
            description: "Perfect for a quick start",
            buttonText: "Start Monthly",
            popular: false
        },
        {
            name: "Annual",
            price: "$99.99",
            period: "/year",
            description: "Best value for professionals",
            buttonText: "Start Annual",
            popular: true
        }
    ];

    return (
        <div style={{
            minHeight: '100vh',
            backgroundColor: '#0A0E27',
            color: '#FFFFFF',
            padding: '40px 20px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            position: 'relative',
            overflow: 'hidden'
        }}>
            {/* Background Glows */}
            <div style={{
                position: 'absolute',
                top: '-10%',
                left: '-10%',
                width: '400px',
                height: '400px',
                background: 'radial-gradient(circle, rgba(108, 92, 231, 0.2) 0%, transparent 70%)',
                zIndex: 0
            }} />
            <div style={{
                position: 'absolute',
                bottom: '10%',
                right: '-5%',
                width: '300px',
                height: '300px',
                background: 'radial-gradient(circle, rgba(162, 155, 254, 0.1) 0%, transparent 70%)',
                zIndex: 0
            }} />

            {/* Header section */}
            <div style={{ textAlign: 'center', marginBottom: '50px', zIndex: 1 }}>
                <div style={{
                    width: '100px',
                    height: '100px',
                    backgroundColor: '#FFFFFF',
                    borderRadius: '24px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 24px',
                    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
                    position: 'relative'
                }}>
                    <span style={{ fontSize: '50px' }}>✨</span>
                </div>
                <h1 style={{ fontSize: '42px', fontWeight: '800', marginBottom: '8px', color: '#FFFFFF' }}>UniVault</h1>
                <div style={{
                    display: 'inline-block',
                    padding: '4px 16px',
                    backgroundColor: 'rgba(255, 215, 0, 0.1)',
                    borderRadius: '20px',
                    border: '1px solid #FFD700',
                    color: '#FFD700',
                    fontSize: '14px',
                    fontWeight: '700',
                    letterSpacing: '1px',
                    marginBottom: '16px'
                }}>PREMIUM</div>
                <p style={{ color: '#B8C5D6', maxWidth: '400px', fontSize: '18px', lineHeight: '1.5' }}>
                    Unlock unlimited potential with premium features designed for your success
                </p>
            </div>

            {/* Features list */}
            <div style={{ width: '100%', maxWidth: '800px', marginBottom: '60px', zIndex: 1 }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
                    {features.map((feature, index) => (
                        <div key={index} style={{
                            backgroundColor: '#1A1F3A',
                            padding: '24px',
                            borderRadius: '24px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '20px',
                            transition: 'transform 0.2s',
                            cursor: 'default',
                            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.2)'
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
                        onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                        >
                            <span style={{ fontSize: '32px' }}>{feature.icon}</span>
                            <div>
                                <h3 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '4px' }}>{feature.title}</h3>
                                <p style={{ fontSize: '14px', color: '#7C8AA8' }}>{feature.description}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Pricing Section */}
            <div style={{ width: '100%', maxWidth: '900px', display: 'flex', flexWrap: 'wrap', gap: '30px', justifyContent: 'center', zIndex: 1, marginBottom: '40px' }}>
                {plans.map((plan, index) => (
                    <div key={index} style={{
                        width: '320px',
                        backgroundColor: plan.popular ? '#6C5CE7' : '#1A1F3A',
                        padding: '40px 30px',
                        borderRadius: '32px',
                        position: 'relative',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        boxShadow: '0 20px 50px rgba(0, 0, 0, 0.3)',
                        border: plan.popular ? '2px solid rgba(255, 255, 255, 0.2)' : 'none'
                    }}>
                        {plan.popular && (
                            <div style={{
                                position: 'absolute',
                                top: '-15px',
                                right: '30px',
                                background: '#FFD700',
                                color: '#000',
                                padding: '4px 12px',
                                borderRadius: '12px',
                                fontSize: '12px',
                                fontWeight: '800'
                            }}>POPULAR</div>
                        )}
                        <h2 style={{ fontSize: '24px', marginBottom: '8px' }}>{plan.name}</h2>
                        <div style={{ display: 'flex', alignItems: 'baseline', marginBottom: '12px' }}>
                            <span style={{ fontSize: '48px', fontWeight: '800' }}>{plan.price}</span>
                            <span style={{ fontSize: '16px', color: plan.popular ? 'rgba(255, 255, 255, 0.8)' : '#7C8AA8' }}>{plan.period}</span>
                        </div>
                        <p style={{ textAlign: 'center', marginBottom: '32px', color: plan.popular ? 'rgba(255, 255, 255, 0.9)' : '#7C8AA8' }}>
                            {plan.description}
                        </p>
                        <button 
                            onClick={() => {
                                alert(`${plan.name} plan selected (Billing integration coming soon)`);
                                navigate('/home');
                            }}
                            style={{
                                width: '100%',
                                padding: '16px',
                                borderRadius: '16px',
                                border: 'none',
                                backgroundColor: plan.popular ? '#FFFFFF' : '#6C5CE7',
                                color: plan.popular ? '#6C5CE7' : '#FFFFFF',
                                fontSize: '16px',
                                fontWeight: '700',
                                cursor: 'pointer',
                                transition: 'all 0.2s'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.opacity = '0.9'}
                            onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
                        >
                            {plan.buttonText}
                        </button>
                    </div>
                ))}
            </div>

            <div style={{ textAlign: 'center', color: '#7C8AA8', fontSize: '14px', zIndex: 1 }}>
                <p>By continuing, you agree to our Terms & Privacy Policy</p>
                <button 
                    onClick={() => navigate('/home')}
                    style={{
                        background: 'none',
                        border: 'none',
                        color: '#6C5CE7',
                        marginTop: '20px',
                        fontSize: '16px',
                        cursor: 'pointer',
                        fontWeight: '600'
                    }}
                >
                    Maybe later
                </button>
            </div>
        </div>
    );
};

export default Subscription;
