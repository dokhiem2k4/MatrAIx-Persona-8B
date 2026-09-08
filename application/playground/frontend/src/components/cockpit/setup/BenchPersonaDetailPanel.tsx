import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { useI18n } from "@/i18n/I18nProvider";
import type { MessageKey } from "@/i18n/types";
import { api, ApiError } from "@/lib/api";
import {
  type DimensionLabelLookup,
  useDimensionLabels,
} from "@/lib/dimensionLabels";
import { personaDisplayId, personaPrimaryName } from "@/lib/personaDisplay";
import {
  PERSONA_BENCH_POOL,
  type PersonaDimensionGroup,
  type PersonaPoolPersonaCard,
} from "@/lib/types";
import { FOCUS_RING, Sym } from "../cockpitShared";
import { PersonaAvatar } from "./PersonaAvatar";
import { personaRosterLines } from "./simulatedPersonaVisual";
import { personaDimChipTone } from "./taskCardLabels";

// Mirrors PERSONA_CARD_DIMENSIONS in the backend's persona_pool_service, which
// leads with locality for a reason: every Vietnamese persona shares "Southeast
// Asia", so that row costs a line and tells the reader nothing, while "Hà Nội"
// vs "Mekong Delta" changes what an in-car assistant gets asked. `intent` is
// dropped entirely -- it is what a persona happens to want in one session, not
// a durable fact about the person, and a profile is read for the latter.
const SPOTLIGHT_KEYS = [
  "age_bracket",
  "vn_locality",
  "life_stage",
  "domain",
  "region",
  // The in-car assistant block. These decide how a persona behaves toward the
  // product under test -- who is listening, how much they hand over, how long
  // they persist -- so a profile that omits them describes the wrong person.
  "vn_usual_companion",
  "vn_voice_privacy_comfort",
  "vn_assistant_task_scope",
  "vn_retry_tolerance",
  "att_voice_assistant",
] as const;

// Partial on purpose: the persona label pack already names every dimension in
// the schema, and dimLabel consults it first. Only the five chrome fields that
// predate the pack need a UI translation of their own, so adding a dimension
// here does not mean adding a key to eight locale files.
const SPOTLIGHT_LABEL_KEYS: Partial<
  Record<(typeof SPOTLIGHT_KEYS)[number], MessageKey>
> = {
  age_bracket: "cockpitSetup.persona.field.age",
  vn_locality: "cockpitSetup.persona.field.locality",
  life_stage: "cockpitSetup.persona.field.lifeStage",
  domain: "cockpitSetup.persona.field.domain",
  region: "cockpitSetup.persona.field.region",
};

export interface BenchPersonaDetailPanelProps {
  persona: PersonaPoolPersonaCard | null;
  /** Pool used to resolve the full YAML / Parquet record. */
  pool?: string | null;
  onClose: () => void;
  onUse?: (persona: PersonaPoolPersonaCard) => void;
  useLabel?: string;
  /** Fill the entire persona rail (hides Model / Dataset / tabs). */
  coverRail?: boolean;
  /** Inline inside the cockpit persona rail — no nested glass card chrome. */
  embedded?: boolean;
  className?: string;
}

function spotlightDotClass(
  tone: ReturnType<typeof personaDimChipTone>,
): string {
  switch (tone) {
    case "primary":
      return "bg-primary/70";
    case "accent":
      return "bg-accent/70";
    case "secondary":
      return "bg-secondary/70";
    case "warn":
      return "bg-warn/70";
    case "danger":
      return "bg-danger/70";
    default:
      return "bg-outline";
  }
}

function TaxonomyTree({
  groups,
  t,
  labels,
}: {
  groups: PersonaDimensionGroup[];
  t: ReturnType<typeof useI18n>["t"];
  labels: DimensionLabelLookup;
}) {
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>(() => {
    const initial: Record<string, boolean> = {};
    groups.forEach((group, index) => {
      // Open only the first group so the panel doesn't start as a dense wall.
      initial[group.id] = index === 0;
    });
    return initial;
  });
  const [openSubgroups, setOpenSubgroups] = useState<Record<string, boolean>>(
    {},
  );

  useEffect(() => {
    const next: Record<string, boolean> = {};
    groups.forEach((group, index) => {
      next[group.id] = index === 0;
    });
    setOpenGroups(next);
    setOpenSubgroups({});
  }, [groups]);

  if (groups.length === 0) {
    return (
      <p className="mt-4 text-[13px] leading-relaxed text-text-dim">
        {t("cockpitSetup.persona.noDimensionValues")}
      </p>
    );
  }

  return (
    <div className="mt-4 space-y-3">
      {groups.map((group) => {
        const groupOpen = openGroups[group.id] ?? false;
        return (
          <section
            key={group.id}
            className="overflow-hidden rounded-xl border border-outline/20 bg-surface/30"
          >
            <button
              type="button"
              aria-expanded={groupOpen}
              onClick={() =>
                setOpenGroups((prev) => ({ ...prev, [group.id]: !groupOpen }))
              }
              className={`flex w-full items-center justify-between gap-3 px-4 py-3.5 text-left transition hover:bg-primary/5 ${FOCUS_RING}`}
            >
              <span className="min-w-0">
                <span className="block font-display text-[14px] font-semibold text-text-main">
                  {labels.taxonomyLabel(group.id, group.label)}
                </span>
                <span className="mt-1 block text-[12px] text-text-dim">
                  {t("cockpitSetup.persona.attributesAndSubgroups", {
                    count: group.count,
                    subgroups: group.subgroups.length,
                  })}
                </span>
              </span>
              <Sym
                name={groupOpen ? "expand_less" : "expand_more"}
                size={20}
                className="shrink-0 text-text-dim"
              />
            </button>
            {groupOpen ? (
              <div className="space-y-2 border-t border-outline/15 px-3 py-3">
                {group.subgroups.map((subgroup) => {
                  const subKey = `${group.id}/${subgroup.id}`;
                  const subOpen = openSubgroups[subKey] ?? false;
                  return (
                    <div key={subgroup.id} className="rounded-lg bg-field/35">
                      <button
                        type="button"
                        aria-expanded={subOpen}
                        onClick={() =>
                          setOpenSubgroups((prev) => ({
                            ...prev,
                            [subKey]: !subOpen,
                          }))
                        }
                        className={`flex w-full items-center justify-between gap-3 px-3.5 py-2.5 text-left ${FOCUS_RING}`}
                      >
                        <span className="text-[13px] font-medium text-text-main">
                          {labels.taxonomyLabel(subgroup.id, subgroup.label)}
                        </span>
                        <span className="flex items-center gap-1.5 text-[12px] text-text-dim">
                          {subgroup.count}
                          <Sym
                            name={subOpen ? "expand_less" : "expand_more"}
                            size={16}
                          />
                        </span>
                      </button>
                      {subOpen ? (
                        <ul className="divide-y divide-outline/10 border-t border-outline/15 px-3.5 py-1">
                          {subgroup.items.map((item) => {
                            const dimLabel = labels.dimLabel(
                              item.id,
                              item.label,
                            );
                            const valueLabel = labels.valueLabel(
                              item.id,
                              item.value,
                            );
                            return (
                            <li
                              key={item.id}
                              className="grid grid-cols-[minmax(0,1fr)_minmax(0,1.15fr)] gap-3 py-2.5"
                            >
                              <span
                                className="truncate text-[12px] leading-snug text-text-dim"
                                title={dimLabel}
                              >
                                {dimLabel}
                              </span>
                              <span
                                className="truncate text-right text-[13px] leading-snug text-text-main"
                                title={valueLabel}
                              >
                                {valueLabel}
                              </span>
                            </li>
                            );
                          })}
                        </ul>
                      ) : null}
                    </div>
                  );
                })}
              </div>
            ) : null}
          </section>
        );
      })}
    </div>
  );
}

export function BenchPersonaDetailPanel({
  persona,
  pool = PERSONA_BENCH_POOL,
  onClose,
  onUse,
  useLabel,
  coverRail = false,
  embedded = false,
  className = "",
}: BenchPersonaDetailPanelProps) {
  const { t } = useI18n();
  const labels = useDimensionLabels();
  const personaId = persona?.personaId ?? null;
  const activePool = pool?.trim() || PERSONA_BENCH_POOL;
  const detailQuery = useQuery({
    queryKey: ["persona-pool-detail", activePool, personaId],
    queryFn: () => api.getPersonaPoolPersona(personaId!, activePool),
    enabled: Boolean(personaId),
    staleTime: 120_000,
    retry: 1,
  });

  const dims = detailQuery.data?.dimensions ?? persona?.dimensions ?? {};
  const groups = useMemo<PersonaDimensionGroup[]>(() => {
    const fromApi = detailQuery.data?.dimensionGroups;
    if (fromApi && fromApi.length > 0) return fromApi;
    const entries = Object.entries(dims);
    if (entries.length === 0) return [];
    return [
      {
        id: "all",
        label: t("cockpitSetup.persona.attributes"),
        count: entries.length,
        subgroups: [
          {
            id: "flat",
            label: t("cockpitSetup.persona.allDimensions"),
            count: entries.length,
            items: entries.map(([id, value]) => ({
              id,
              label: labels.dimLabel(id, id.replace(/_/g, " ")),
              value: labels.valueLabel(id, value),
            })),
          },
        ],
      },
    ];
  }, [detailQuery.data?.dimensionGroups, dims, t, labels]);

  const spotlight = useMemo(
    () =>
      SPOTLIGHT_KEYS.map((key) => {
        const raw = dims[key];
        if (!raw) return null;
        // Region is the coarse fallback, shown only when the persona has no
        // locality. Rendering both would put "Hà Nội" and "Southeast Asia" on
        // consecutive rows, where the second says nothing the first did not.
        if (key === "region" && dims.vn_locality) return null;
        return {
          key,
          label: labels.dimLabel(
            key,
            SPOTLIGHT_LABEL_KEYS[key]
              ? t(SPOTLIGHT_LABEL_KEYS[key] as MessageKey)
              : key.replace(/_/g, " "),
          ),
          value: labels.valueLabel(key, raw),
        };
      }).filter((item): item is { key: (typeof SPOTLIGHT_KEYS)[number]; label: string; value: string } =>
        Boolean(item),
      ),
    [dims, t, labels],
  );

  if (!persona) return null;

  const displayName = personaPrimaryName(persona.name, persona.personaId, dims);
  const codename = personaDisplayId(persona.personaId);
  const roster = personaRosterLines(dims);
  const blurb = roster
    ? roster.secondary
      ? `${roster.primary} · ${roster.secondary}`
      : roster.primary
    : null;
  const poolLabel =
    detailQuery.data?.pool?.trim() ||
    detailQuery.data?.path?.trim() ||
    activePool;
  const filledCount =
    detailQuery.data?.dimensionGroups?.reduce(
      (sum, group) => sum + group.count,
      0,
    ) ?? Object.keys(dims).length;

  const shellClass = coverRail
    ? `flex h-full min-h-0 w-full flex-col overflow-hidden ${className}`
    : embedded
      ? `flex h-full min-h-0 w-full flex-col overflow-hidden ${className}`
      : `glass-panel flex h-full max-h-full min-h-0 min-w-0 flex-col overflow-hidden rounded-xl ${className}`;

  return (
    <aside
      className={shellClass}
      aria-label={t("cockpitSetup.persona.detailsFor", { name: displayName })}
    >
      <div className="shrink-0 border-b border-outline/20 px-1 pb-3 pt-0.5">
        <div className="flex items-center justify-between gap-2">
          <button
            type="button"
            onClick={onClose}
            className={`inline-flex items-center gap-1 rounded-md px-2 py-1.5 text-[13px] font-medium text-text-dim transition hover:bg-surface-high hover:text-text-main ${FOCUS_RING}`}
          >
            <Sym name="arrow_back" size={16} />
            {t("cockpitSetup.common.back")}
          </button>
          <p className="cockpit-field-label text-[11px] tracking-[0.08em] text-text-dim">
            {t("cockpitSetup.persona.profile")}
          </p>
          <button
            type="button"
            onClick={onClose}
            aria-label={t("cockpitSetup.persona.closeDetails")}
            className={`shrink-0 rounded-md p-1.5 text-text-dim transition hover:bg-surface-high hover:text-text-main ${FOCUS_RING}`}
          >
            <Sym name="close" size={18} />
          </button>
        </div>
      </div>

      <div className="custom-scrollbar min-h-0 flex-1 overflow-y-auto overscroll-contain px-1 pt-5">
        <div className="flex items-start gap-4">
          <PersonaAvatar
            personaId={persona.personaId}
            dimensions={dims}
            size="lg"
          />
          <div className="min-w-0 flex-1 pt-0.5">
            <h2 className="font-display text-[20px] font-semibold leading-tight text-text-main">
              {displayName}
            </h2>
            <p className="mt-1 flex min-w-0 flex-wrap items-center gap-x-1.5 gap-y-0.5 text-[12px] leading-snug text-text-dim">
              <span className="font-mono tracking-wide">{codename}</span>
              {persona.source ? (
                <>
                  <span className="text-outline/80" aria-hidden>
                    ·
                  </span>
                  <span>{persona.source}</span>
                </>
              ) : null}
              {filledCount > 0 ? (
                <>
                  <span className="text-outline/80" aria-hidden>
                    ·
                  </span>
                  <span>
                    {t("cockpitSetup.persona.dimensionsCount", {
                      count: filledCount,
                    })}
                  </span>
                </>
              ) : null}
            </p>
          </div>
        </div>

        {blurb ? (
          <p className="mt-4 text-[14px] leading-relaxed text-text-variant">
            {blurb}
          </p>
        ) : null}

        {spotlight.length > 0 ? (
          <dl className="mt-5 space-y-3 border-y border-outline/20 py-4">
            {spotlight.map(({ key, label, value }, index) => (
              <div
                key={key}
                // Labels here are dimension names, several of which are longer
                // than their values ("Thoải mái khi có người" vs "Thoải mái").
                // A narrow label column wrapped them to four lines while the
                // value column sat half empty, so the label side gets the room.
                className="grid grid-cols-[9rem_1fr] items-baseline gap-x-3"
              >
                <dt className="text-[12px] text-text-dim">
                  <span
                    className={`mr-1.5 inline-block h-1.5 w-1.5 rounded-full align-middle ${spotlightDotClass(personaDimChipTone(key, index))}`}
                    aria-hidden
                  />
                  {label}
                </dt>
                <dd
                  className="min-w-0 text-[14px] leading-snug text-text-main"
                  title={value}
                >
                  {value}
                </dd>
              </div>
            ))}
          </dl>
        ) : null}

        <div className="mt-6">
          <div>
            <p className="font-display text-[15px] font-semibold text-text-main">
              {t("cockpitSetup.persona.taxonomy")}
            </p>
            <p className="mt-1 text-[12px] leading-relaxed text-text-dim">
              {t("cockpitSetup.persona.groupsBrowse", { count: groups.length })}
            </p>
          </div>
          {detailQuery.isPending ? (
            <p className="mt-4 text-[13px] text-text-dim">
              {t("cockpitSetup.persona.loadingDimensions")}
            </p>
          ) : null}
          {detailQuery.isError ? (
            <p className="mt-4 text-[13px] text-danger">
              {detailQuery.error instanceof ApiError
                ? detailQuery.error.message
                : t("cockpitSetup.persona.loadRecordFailed")}
            </p>
          ) : null}
          {!detailQuery.isPending ? (
            <TaxonomyTree groups={groups} t={t} labels={labels} />
          ) : null}
        </div>

        <p className="mt-6 pb-4 font-mono text-[11px] leading-relaxed text-text-dim">
          {poolLabel}
        </p>
      </div>

      {onUse ? (
        <div className="shrink-0 border-t border-outline/25 px-1 py-3.5">
          <button
            type="button"
            onClick={() => onUse(persona)}
            className={`inline-flex h-10 w-full items-center justify-center rounded-md bg-primary text-[14px] font-medium text-on-primary transition hover:bg-primary/90 ${FOCUS_RING}`}
          >
            {useLabel ?? t("cockpitSetup.persona.use")}
          </button>
        </div>
      ) : null}
    </aside>
  );
}
