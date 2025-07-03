import React from 'react';
import { Link } from 'react-router-dom';
import { Upload, Zap, Download } from 'lucide-react';
import Stepper from '../components/Stepper';

const HomePage: React.FC = () => {
  const steps = [
    {
      icon: Upload,
      title: "Upload Images",
      description: "Simply upload your images for our AI to analyze and generate 3D models.",
    },
    {
      icon: Zap,
      title: "AI Processing",
      description: "Our AI processes your images and generates detailed 3D models.",
    },
    {
      icon: Download,
      title: "Download Models",
      description: "Download your 3D models and use them in your projects.",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Hero Section */}
      <section className="text-center py-20">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            Transform Images into 3D Models
          </h1>
          <p className="text-xl text-gray-400 mb-8 max-w-3xl mx-auto">
            Harness the power of AI to convert your 2D images into stunning 3D models. Perfect for game development, 3D printing, and digital art projects.
          </p>
          <Link
            to="/upload"
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Start Creating
          </Link>
        </div>
      </section>

      {/* "How It Works" Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              How It Works
            </h2>
          </div>
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <Stepper steps={steps} />
            <div>
              <img src="/placeholder.png" alt="3D Model" className="rounded-lg" />
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gray-800 py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
            Get started with your first 3D model today.
          </p>
          <Link
            to="/upload"
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors inline-block"
          >
            Upload Image
          </Link>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
