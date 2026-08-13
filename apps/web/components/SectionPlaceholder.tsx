type SectionPlaceholderProps = {
  title: string;
  description: string;
};

export function SectionPlaceholder({ title, description }: SectionPlaceholderProps) {
  return (
    <section className="placeholder-card">
      <p className="eyebrow">Foundation area</p>
      <h1>{title}</h1>
      <p>{description}</p>
    </section>
  );
}
