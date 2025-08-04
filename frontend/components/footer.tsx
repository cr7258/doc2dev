import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-gray-200 bg-white py-4">
      <div className="container mx-auto px-4 max-w-5xl">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div>
            © 2025 Doc2Dev. All rights reserved.
          </div>
          <div>
            <a
              href="https://github.com/cr7258/doc2dev"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center text-gray-500 hover:text-gray-700 transition-colors duration-200"
              aria-label="GitHub repository"
            >
              <img src="/github.svg" alt="GitHub" className="h-5 w-5" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
