import * as React from "react"
import * as ProgressPrimitive from "@radix-ui/react-progress"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/utils/cn"

const progressVariants = cva(
  "relative h-4 w-full overflow-hidden rounded-full bg-secondary transition-all duration-200",
  {
    variants: {
      size: {
        sm: "h-2",
        default: "h-4",
        lg: "h-6",
      },
      variant: {
        default: "bg-secondary",
        success: "bg-green-200 dark:bg-green-900",
        warning: "bg-yellow-200 dark:bg-yellow-900",
        error: "bg-red-200 dark:bg-red-900",
      },
    },
    defaultVariants: {
      size: "default",
      variant: "default",
    },
  }
)

const progressIndicatorVariants = cva(
  "h-full w-full flex-1 bg-primary transition-all duration-300 ease-in-out",
  {
    variants: {
      variant: {
        default: "bg-primary",
        success: "bg-green-600 dark:bg-green-500",
        warning: "bg-yellow-600 dark:bg-yellow-500",
        error: "bg-red-600 dark:bg-red-500",
      },
      animated: {
        true: "animate-pulse",
        false: "",
      },
    },
    defaultVariants: {
      variant: "default",
      animated: false,
    },
  }
)

export interface ProgressProps
  extends React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root>,
    VariantProps<typeof progressVariants> {
  value?: number
  max?: number
  animated?: boolean
  showValue?: boolean
  label?: string
  description?: string
}

const Progress = React.forwardRef<
  React.ElementRef<typeof ProgressPrimitive.Root>,
  ProgressProps
>(({ 
  className, 
  value = 0, 
  max = 100, 
  size, 
  variant, 
  animated = false, 
  showValue = false,
  label,
  description,
  ...props 
}, ref) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)
  const progressId = React.useId()
  
  return (
    <div className="w-full">
      {(label || description) && (
        <div className="mb-2 flex items-center justify-between">
          {label && (
            <label 
              htmlFor={progressId}
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
              {label}
            </label>
          )}
          {showValue && (
            <span className="text-sm text-muted-foreground">
              {Math.round(percentage)}%
            </span>
          )}
        </div>
      )}
      
      {description && (
        <p className="text-sm text-muted-foreground mb-2">
          {description}
        </p>
      )}
      
      <ProgressPrimitive.Root
        ref={ref}
        id={progressId}
        className={cn(progressVariants({ size, variant, className }))}
        value={value}
        max={max}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-valuenow={value}
        aria-valuetext={`${Math.round(percentage)}%`}
        role="progressbar"
        {...props}
      >
        <ProgressPrimitive.Indicator
          className={cn(progressIndicatorVariants({ variant, animated }))}
          style={{ transform: `translateX(-${100 - percentage}%)` }}
        />
      </ProgressPrimitive.Root>
    </div>
  )
})
Progress.displayName = ProgressPrimitive.Root.displayName

// Additional Progress variants for different use cases
const CircularProgress = React.forwardRef<
  HTMLDivElement,
  {
    value?: number
    max?: number
    size?: number
    strokeWidth?: number
    variant?: "default" | "success" | "warning" | "error"
    showValue?: boolean
    className?: string
  }
>(({ 
  value = 0, 
  max = 100, 
  size = 120, 
  strokeWidth = 8, 
  variant = "default",
  showValue = false,
  className,
  ...props 
}, ref) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const strokeDashoffset = circumference - (percentage / 100) * circumference
  
  const getStrokeColor = () => {
    switch (variant) {
      case "success": return "stroke-green-600 dark:stroke-green-500"
      case "warning": return "stroke-yellow-600 dark:stroke-yellow-500"
      case "error": return "stroke-red-600 dark:stroke-red-500"
      default: return "stroke-primary"
    }
  }
  
  return (
    <div 
      ref={ref}
      className={cn("relative inline-flex items-center justify-center", className)}
      style={{ width: size, height: size }}
      {...props}
    >
      <svg
        className="transform -rotate-90"
        width={size}
        height={size}
      >
        <circle
          className="stroke-secondary"
          strokeWidth={strokeWidth}
          fill="transparent"
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
        <circle
          className={cn("transition-all duration-300 ease-in-out", getStrokeColor())}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          fill="transparent"
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
      </svg>
      {showValue && (
        <span className="absolute text-xl font-semibold">
          {Math.round(percentage)}%
        </span>
      )}
    </div>
  )
})
CircularProgress.displayName = "CircularProgress"

// Multi-step Progress component
export interface Step {
  label: string
  description?: string
  completed?: boolean
  active?: boolean
}

const StepProgress = React.forwardRef<
  HTMLDivElement,
  {
    steps: Step[]
    currentStep?: number
    variant?: "default" | "success" | "warning" | "error"
    orientation?: "horizontal" | "vertical"
    className?: string
  }
>(({ 
  steps, 
  currentStep = 0, 
  variant = "default", 
  orientation = "horizontal",
  className,
  ...props 
}, ref) => {
  const getStepStatus = (index: number) => {
    if (steps[index]?.completed || index < currentStep) return "completed"
    if (steps[index]?.active || index === currentStep) return "active"
    return "pending"
  }
  
  const getStepColor = (status: string) => {
    if (status === "completed") {
      switch (variant) {
        case "success": return "bg-green-600 border-green-600 text-white"
        case "warning": return "bg-yellow-600 border-yellow-600 text-white"
        case "error": return "bg-red-600 border-red-600 text-white"
        default: return "bg-primary border-primary text-primary-foreground"
      }
    }
    if (status === "active") {
      return "bg-background border-primary text-primary ring-2 ring-primary ring-offset-2"
    }
    return "bg-muted border-muted-foreground/25 text-muted-foreground"
  }
  
  const getConnectorColor = (index: number) => {
    const status = getStepStatus(index)
    if (status === "completed") {
      switch (variant) {
        case "success": return "bg-green-600"
        case "warning": return "bg-yellow-600"
        case "error": return "bg-red-600"
        default: return "bg-primary"
      }
    }
    return "bg-muted"
  }
  
  return (
    <div 
      ref={ref}
      className={cn(
        "flex",
        orientation === "horizontal" ? "items-center" : "flex-col",
        className
      )}
      {...props}
    >
      {steps.map((step, index) => (
        <React.Fragment key={index}>
          <div className={cn(
            "flex items-center",
            orientation === "vertical" && "flex-col text-center"
          )}>
            <div
              className={cn(
                "flex h-8 w-8 items-center justify-center rounded-full border-2 text-sm font-medium transition-all duration-200",
                getStepColor(getStepStatus(index))
              )}
            >
              {getStepStatus(index) === "completed" ? (
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <span>{index + 1}</span>
              )}
            </div>
            
            <div className={cn(
              "ml-3",
              orientation === "vertical" && "ml-0 mt-2"
            )}>
              <p className="text-sm font-medium">{step.label}</p>
              {step.description && (
                <p className="text-xs text-muted-foreground">{step.description}</p>
              )}
            </div>
          </div>
          
          {index < steps.length - 1 && (
            <div
              className={cn(
                "transition-all duration-200",
                orientation === "horizontal" 
                  ? "mx-4 h-0.5 flex-1" 
                  : "my-4 h-8 w-0.5 self-center",
                getConnectorColor(index)
              )}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  )
})
StepProgress.displayName = "StepProgress"

export { Progress, CircularProgress, StepProgress, progressVariants, progressIndicatorVariants }