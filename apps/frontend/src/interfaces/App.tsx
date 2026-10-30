const MAIN_ID = 'main-content';

export function App() {
  return (
    <>
      <a className="skip-link" href={`#${MAIN_ID}`}>
        Skip to main content
      </a>
      <header className="app-header">
        <p className="app-name">Project generator</p>
      </header>
      <main id={MAIN_ID} tabIndex={-1}>
        <h1>Create a development project</h1>
        <p>The guided project creation will be available here.</p>
      </main>
    </>
  );
}
