import { BackendStatus } from "@/features/health/BackendStatus";

export default function HomePage() {
  return (
    <section className="hero">
      <p className="eyebrow">Creator intelligence foundation</p>
      <h1>CREATOR OS</h1>
      <p className="lead">
        AI-powered Creator Intelligence, Strategy and Content Operating System.
      </p>
      <p className="success">Frontend foundation is running.</p>
      <BackendStatus />
    </section>
  );
}
