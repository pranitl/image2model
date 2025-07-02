import React, { useState } from 'react'
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Progress,
  CircularProgress,
  StepProgress,
  Toaster
} from '@/components'
import { toastSuccess, toastError, toastWarning, toastInfo } from '@/hooks'
import { Upload, Download, Heart, AlertCircle, CheckCircle, Info } from 'lucide-react'

const ComponentShowcase: React.FC = () => {
  const [progress, setProgress] = useState(45)
  const [circularProgress, setCircularProgress] = useState(65)
  const [currentStep, setCurrentStep] = useState(1)
  const [darkMode, setDarkMode] = useState(false)

  const steps = [
    { label: 'Upload Image', description: 'Select and upload your image file' },
    { label: 'Process Image', description: 'AI processes your image', active: true },
    { label: 'Generate Model', description: 'Create 3D model from image' },
    { label: 'Download', description: 'Download your 3D model' }
  ]

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
    document.documentElement.classList.toggle('dark')
  }

  const showToastExamples = () => {
    toastSuccess('Success!', 'Your 3D model has been generated successfully.')
    setTimeout(() => {
      toastWarning('Warning', 'Processing may take longer for high resolution images.')
    }, 1000)
    setTimeout(() => {
      toastInfo('Info', 'Your model will be available for download for 24 hours.')
    }, 2000)
    setTimeout(() => {
      toastError('Error', 'Failed to process image. Please try again.')
    }, 3000)
  }

  return (
    <div className={`min-h-screen bg-background text-foreground transition-colors duration-200 ${darkMode ? 'dark' : ''}`}>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">UI Component Showcase</h1>
            <p className="text-muted-foreground mt-2">
              Demonstrating all UI components with accessibility and dark theme support
            </p>
          </div>
          <Button onClick={toggleDarkMode} variant="outline" size="lg">
            {darkMode ? '☀️' : '🌙'} Toggle Theme
          </Button>
        </div>

        {/* Button Components */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Button Component</CardTitle>
            <CardDescription>
              Enhanced button component with loading states, icons, and accessibility features
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-3">
              <Button>Default</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="link">Link</Button>
              <Button variant="destructive">Destructive</Button>
              <Button variant="success">Success</Button>
              <Button variant="warning">Warning</Button>
            </div>
            
            <div className="flex flex-wrap gap-3">
              <Button size="xs">Extra Small</Button>
              <Button size="sm">Small</Button>
              <Button size="default">Default</Button>
              <Button size="lg">Large</Button>
              <Button size="icon">
                <Heart className="h-4 w-4" />
              </Button>
            </div>

            <div className="flex flex-wrap gap-3">
              <Button leftIcon={<Upload className="h-4 w-4" />}>
                Upload
              </Button>
              <Button rightIcon={<Download className="h-4 w-4" />} variant="outline">
                Download
              </Button>
              <Button loading>Loading...</Button>
              <Button disabled>Disabled</Button>
            </div>
          </CardContent>
        </Card>

        {/* Card Components */}
        <Card variant="elevated" className="mb-8">
          <CardHeader>
            <CardTitle level={2}>Card Component</CardTitle>
            <CardDescription>
              Flexible card component with multiple variants and configurable padding
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Card variant="default">
                <CardHeader padding="sm">
                  <CardTitle level={4}>Default Card</CardTitle>
                  <CardDescription>Standard card with default styling</CardDescription>
                </CardHeader>
                <CardContent padding="sm">
                  <p className="text-sm">This is a default card with small padding.</p>
                </CardContent>
                <CardFooter padding="sm">
                  <Button size="sm">Action</Button>
                </CardFooter>
              </Card>

              <Card variant="outlined">
                <CardHeader>
                  <CardTitle level={4}>Outlined Card</CardTitle>
                  <CardDescription>Card with prominent border</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm">This is an outlined card with default padding.</p>
                </CardContent>
                <CardFooter justify="between">
                  <Button variant="ghost" size="sm">Cancel</Button>
                  <Button size="sm">Confirm</Button>
                </CardFooter>
              </Card>

              <Card variant="ghost">
                <CardHeader>
                  <CardTitle level={4}>Ghost Card</CardTitle>
                  <CardDescription>Subtle card without borders or shadows</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm">This is a ghost card with minimal styling.</p>
                </CardContent>
              </Card>
            </div>
          </CardContent>
        </Card>

        {/* Progress Components */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Progress Components</CardTitle>
            <CardDescription>
              Various progress indicators for different use cases
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Linear Progress */}
            <div>
              <h4 className="font-semibold mb-4">Linear Progress</h4>
              <div className="space-y-4">
                <Progress 
                  value={progress} 
                  label="Processing Image" 
                  description="Converting your image to 3D model"
                  showValue 
                />
                
                <div className="flex gap-4">
                  <Progress value={75} variant="success" size="sm" showValue />
                  <Progress value={50} variant="warning" size="default" showValue />
                  <Progress value={25} variant="error" size="lg" showValue />
                </div>

                <Progress value={80} animated showValue />
                
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => setProgress(Math.max(0, progress - 10))}>
                    Decrease
                  </Button>
                  <Button size="sm" onClick={() => setProgress(Math.min(100, progress + 10))}>
                    Increase
                  </Button>
                </div>
              </div>
            </div>

            {/* Circular Progress */}
            <div>
              <h4 className="font-semibold mb-4">Circular Progress</h4>
              <div className="flex items-center gap-8">
                <CircularProgress 
                  value={circularProgress} 
                  showValue 
                  size={100}
                />
                <CircularProgress 
                  value={80} 
                  variant="success" 
                  showValue 
                  size={80}
                  strokeWidth={6}
                />
                <CircularProgress 
                  value={60} 
                  variant="warning" 
                  showValue 
                  size={120}
                  strokeWidth={10}
                />
                
                <div className="flex flex-col gap-2">
                  <Button size="sm" onClick={() => setCircularProgress(Math.max(0, circularProgress - 10))}>
                    Decrease
                  </Button>
                  <Button size="sm" onClick={() => setCircularProgress(Math.min(100, circularProgress + 10))}>
                    Increase
                  </Button>
                </div>
              </div>
            </div>

            {/* Step Progress */}
            <div>
              <h4 className="font-semibold mb-4">Step Progress</h4>
              <div className="space-y-6">
                <StepProgress 
                  steps={steps} 
                  currentStep={currentStep}
                  variant="default"
                />
                
                <StepProgress 
                  steps={[
                    { label: 'Setup', completed: true },
                    { label: 'Configuration', completed: true },
                    { label: 'Testing', active: true },
                    { label: 'Deployment' }
                  ]} 
                  orientation="vertical"
                  variant="success"
                />
                
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}>
                    Previous Step
                  </Button>
                  <Button size="sm" onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))}>
                    Next Step
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Toast Components */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Toast Notifications</CardTitle>
            <CardDescription>
              Accessible toast notifications with different variants and automatic dismissal
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              <Button 
                onClick={() => toastSuccess('Success!', 'Operation completed successfully.')}
                leftIcon={<CheckCircle className="h-4 w-4" />}
                variant="success"
              >
                Success Toast
              </Button>
              
              <Button 
                onClick={() => toastError('Error!', 'Something went wrong. Please try again.')}
                leftIcon={<AlertCircle className="h-4 w-4" />}
                variant="destructive"
              >
                Error Toast
              </Button>
              
              <Button 
                onClick={() => toastWarning('Warning!', 'This action may take some time.')}
                leftIcon={<AlertCircle className="h-4 w-4" />}
                variant="warning"
              >
                Warning Toast
              </Button>
              
              <Button 
                onClick={() => toastInfo('Info', 'Here is some helpful information.')}
                leftIcon={<Info className="h-4 w-4" />}
                variant="outline"
              >
                Info Toast
              </Button>
              
              <Button 
                onClick={showToastExamples}
                variant="outline"
              >
                Show All Toast Types
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Accessibility Features */}
        <Card>
          <CardHeader>
            <CardTitle>Accessibility Features</CardTitle>
            <CardDescription>
              All components include proper ARIA attributes, keyboard navigation, and screen reader support
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 border rounded-lg">
                <h4 className="font-semibold mb-2">Keyboard Navigation</h4>
                <p className="text-sm text-muted-foreground mb-3">
                  All interactive components support keyboard navigation with Tab, Enter, and Space keys.
                </p>
                <div className="flex gap-2">
                  <Button onKeyDown={(e) => e.key === 'Enter' && console.log('Enter pressed')}>
                    Tab Navigation
                  </Button>
                  <Button variant="outline">
                    Focus Test
                  </Button>
                </div>
              </div>
              
              <div className="p-4 border rounded-lg">
                <h4 className="font-semibold mb-2">Screen Reader Support</h4>
                <p className="text-sm text-muted-foreground mb-3">
                  Components include proper ARIA labels, descriptions, and live regions for screen readers.
                </p>
                <Progress 
                  value={75} 
                  label="Processing with screen reader support"
                  aria-describedby="progress-description"
                />
                <p id="progress-description" className="text-xs text-muted-foreground mt-2">
                  Progress bar with proper ARIA attributes for accessibility
                </p>
              </div>

              <div className="p-4 border rounded-lg">
                <h4 className="font-semibold mb-2">Dark Theme Support</h4>
                <p className="text-sm text-muted-foreground mb-3">
                  All components adapt to dark theme with proper contrast ratios and visibility.
                </p>
                <Button onClick={toggleDarkMode} leftIcon={darkMode ? <span>☀️</span> : <span>🌙</span>}>
                  {darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <Toaster />
    </div>
  )
}

export default ComponentShowcase