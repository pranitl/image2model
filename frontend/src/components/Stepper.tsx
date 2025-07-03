import React from 'react';
import { Icon } from 'lucide-react';

interface StepProps {
  icon: Icon;
  title: string;
  description: string;
  isActive?: boolean;
}

const Stepper: React.FC<{ steps: Omit<StepProps, 'isActive'>[] }> = ({ steps }) => {
  return (
    <div className="relative">
      {steps.map((step, index) => (
        <div key={index} className="flex items-start mb-8">
          <div className="flex flex-col items-center mr-4">
            <div className={`w-12 h-12 rounded-full flex items-center justify-center ${index === 1 ? 'bg-blue-600' : 'bg-gray-700'}`}>
              <step.icon className="h-6 w-6 text-white" />
            </div>
            {index < steps.length - 1 && (
              <div className="w-px h-16 bg-gray-600 mt-2"></div>
            )}
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
            <p className="text-gray-400">{step.description}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default Stepper;
