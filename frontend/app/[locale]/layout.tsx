import { notFound } from "next/navigation";
import { Locale, isValidLocale, getDirection, SUPPORTED_LOCALES } from "@/lib/i18n/config";
import { DirectionProvider } from "@/components/layout/DirectionProvider";
import { Shell } from "@/components/layout/Shell";

export async function generateStaticParams() {
  return SUPPORTED_LOCALES.map((locale) => ({ locale }));
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;

  if (!isValidLocale(locale)) {
    notFound();
  }

  const validLocale = locale as Locale;
  const direction = getDirection(validLocale);

  return (
    <html lang={validLocale} dir={direction} className="dark">
      <body className="bg-obsidian-950 text-brand-text min-h-screen">
        <DirectionProvider locale={validLocale}>
          <Shell>{children}</Shell>
        </DirectionProvider>
      </body>
    </html>
  );
}
