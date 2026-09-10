// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { RunLaunchBar } from "../RunLaunchBar";
import { I18nProvider } from "../../../../i18n/I18nProvider";

/**
 * The number on this button is what the run costs. A case-driven task runs one
 * trial per persona x scenario, and showing the cohort size instead understated
 * a 15-scenario task list by 15x.
 */
function renderBar(props: Partial<Parameters<typeof RunLaunchBar>[0]>) {
  return render(
    <I18nProvider>
      <RunLaunchBar
        canRun
        isBatch
        personaCount={3}
        parallelTrials={2}
        onParallelTrialsChange={() => {}}
        isRunning={false}
        onRun={() => {}}
        {...props}
      />
    </I18nProvider>,
  );
}

afterEach(cleanup);

describe("RunLaunchBar trial count", () => {
  it("multiplies personas by the task's scenarios", () => {
    renderBar({ caseCount: 15, caseSampleSize: 15 });

    expect(screen.getByRole("button", { name: /45/ })).toBeTruthy();
  });

  it("follows a capped scenario count", () => {
    renderBar({ caseCount: 15, caseSampleSize: 4, onCaseSampleSizeChange: () => {} });

    expect(screen.getByRole("button", { name: /12/ })).toBeTruthy();
  });

  it("stays at one trial per persona when the task ships no scenarios", () => {
    renderBar({ caseCount: 0 });

    expect(screen.getByRole("button", { name: /\b3\b/ })).toBeTruthy();
  });
});
