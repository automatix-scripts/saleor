// /home/ubuntu/user-panel/components/ui/Input.tsx
// Autor: Szymon Fuchs
// Data: 04.08.2021
import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  className?: string;
}

const Input: React.FC<InputProps> = ({ className = '', ...props }) => {
  return (
    <input
      className={`appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${className}`}
      {...props}
    />
  );
};

export default Input;
