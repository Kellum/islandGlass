import { useRef, useEffect, useState } from 'react';
import { animate } from 'animejs';

export function useAnimatedValue(targetValue: number, duration: number = 400) {
  const [displayValue, setDisplayValue] = useState(targetValue);
  const currentRef = useRef(targetValue);

  useEffect(() => {
    if (currentRef.current === targetValue) return;

    const obj = { value: currentRef.current };
    animate(obj, {
      value: targetValue,
      duration,
      ease: 'outQuart',
      onUpdate: () => {
        setDisplayValue(obj.value);
      },
      onComplete: () => {
        currentRef.current = targetValue;
        setDisplayValue(targetValue);
      },
    });
  }, [targetValue, duration]);

  return displayValue;
}
