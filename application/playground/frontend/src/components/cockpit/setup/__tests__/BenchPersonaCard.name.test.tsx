// @vitest-environment jsdom
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { BenchPersonaCard } from "../BenchPersonaCard";
import { I18nProvider } from "../../../../i18n/I18nProvider";

/**
 * These assert the name and id are RENDERED. They do NOT catch the bug that
 * prompted them -- the name was in the DOM the whole time, collapsed to 0px by
 * a flex sibling that refused to shrink. jsdom performs no layout, so every
 * box here is 0x0 and these pass either way. Verified by deleting the fix and
 * watching them stay green.
 *
 * The layout itself is measured in real Chrome by
 * `scripts/measure_persona_cards.py`, which reads getBoundingClientRect and
 * fails when a name is zero-width or clipped.
 */
const LONG_SOURCE = "vn_driver_survey_2026+wvs_wave7_vnm_2020";

function renderCard(source: string) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <I18nProvider>
      <BenchPersonaCard
      persona={{
        personaId: "vn-drv-001",
        name: "Bùi Minh Châu",
        source,
        dimensions: { age_bracket: "35-44", vn_locality: "Hai Phong" },
        }}
      />
      </I18nProvider>
    </QueryClientProvider>,
  );
}

afterEach(cleanup);

describe("BenchPersonaCard name", () => {
  it("renders the name when the source label is long", () => {
    renderCard(LONG_SOURCE);
    expect(screen.getByText("Bùi Minh Châu")).toBeTruthy();
  });

  it("renders the name when the source label is short", () => {
    renderCard("wiki");
    expect(screen.getByText("Bùi Minh Châu")).toBeTruthy();
  });

  it("still shows the id as a codename", () => {
    renderCard(LONG_SOURCE);
    expect(screen.getByText("persona-vn-drv-001")).toBeTruthy();
  });
});
