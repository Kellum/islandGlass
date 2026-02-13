import { useRef, useEffect, useState } from 'react';
import { animate } from 'animejs';
import { cn } from '../../utils/cn';

interface AnimatedPriceProps {
  value: number;
  className?: string;
  prefix?: string;
  duration?: number;
}

export function AnimatedPrice({
  value,
  className,
  prefix = '$',
  duration = 400,
}: AnimatedPriceProps) {
  const [displayValue, setDisplayValue] = useState(value);
  const [flash, setFlash] = useState(false);
  const currentRef = useRef(value);
  const elRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (currentRef.current === value) return;

    // Flash effect on change
    setFlash(true);
    const flashTimer = setTimeout(() => setFlash(false), 300);

    // Scale pulse
    if (elRef.current) {
      animate(elRef.current, {
        scale: [1, 1.05, 1],
        duration: 300,
        ease: 'outQuad',
      });
    }

    // Number counter animation
    const obj = { val: currentRef.current };
    animate(obj, {
      val: value,
      duration,
      ease: 'outQuart',
      onUpdate: () => setDisplayValue(obj.val),
      onComplete: () => {
        currentRef.current = value;
        setDisplayValue(value);
      },
    });

    return () => {
      clearTimeout(flashTimer);
    };
  }, [value, duration]);

  return (
    <span
      ref={elRef}
      className={cn(
        'inline-block tabular-nums transition-colors duration-300',
        flash && 'text-green-600',
        className
      )}
    >
      {prefix}
      {displayValue.toFixed(2)}
    </span>
  );
}
