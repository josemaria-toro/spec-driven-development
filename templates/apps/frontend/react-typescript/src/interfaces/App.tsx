import { APP_NAME, PAGE_HEADING, PAGE_INTRODUCTION } from '@/domain/page-content';

const MAIN_ID = 'main-content';

export function App() {
  return (
    <>
      <a className="skip-link" href={`#${MAIN_ID}`}>
        Skip to main content
      </a>
      <header className="app-header">
        <p className="app-name">{APP_NAME}</p>
      </header>
      <main id={MAIN_ID} tabIndex={-1}>
        <h1>{PAGE_HEADING}</h1>
        <p>{PAGE_INTRODUCTION}</p>
      </main>
    </>
  );
}
