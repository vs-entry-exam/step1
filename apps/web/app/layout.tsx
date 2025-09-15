export const metadata = {
  title: 'Step1 RAG QA',
  description: 'Document QA with sources',
};

import './globals.css';
import { ModeToggle } from '../components/ModeToggle';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="container">
          <div className="header">
            <h1 style={{ margin: 0 }}>Step1 RAG QA</h1>
            <ModeToggle />
          </div>
          {children}
        </div>
      </body>
    </html>
  );
}
