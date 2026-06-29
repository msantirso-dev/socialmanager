import { Suspense } from "react";
import SocialPageInner from "./social-client";

export default function SocialPage() {
  return (
    <Suspense fallback={<div className="p-8">Cargando...</div>}>
      <SocialPageInner />
    </Suspense>
  );
}
