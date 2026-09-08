import { FOCUS_RING, Sym } from "../cockpitShared";
import { useI18n } from "@/i18n/I18nProvider";
import type { MessageKey } from "@/i18n/types";
import { useDimensionLabels } from "@/lib/dimensionLabels";
import { personaDisplayId, personaPrimaryName } from "@/lib/personaDisplay";
import type { PersonaPoolPersonaCard } from "@/lib/types";
import { PersonaAvatar } from "./PersonaAvatar";
import type { PersonaSearchHit } from "./personaSearchHits";
import { CHIP_TEXT_CLASS, personaDimChipTone } from "./taskCardLabels";
import { ToneChip } from "./ToneChip";

const DIM_LABEL_KEYS: Record<string, MessageKey> = {
  age_bracket: "cockpitSetup.persona.field.age",
  vn_locality: "cockpitSetup.persona.field.locality",
  region: "cockpitSetup.persona.field.region",
  domain: "cockpitSetup.persona.field.domain",
  intent: "cockpitSetup.persona.field.intent",
  life_stage: "cockpitSetup.persona.field.lifeStage",
  source: "cockpitSetup.persona.field.source",
};

export interface BenchPersonaCardProps {
  persona: PersonaPoolPersonaCard;
  selected?: boolean;
  disabled?: boolean;
  onToggle?: () => void;
  onOpenDetail?: () => void;
  /** Attribute hits explaining why this card matched the current query. */
  hits?: PersonaSearchHit[];
}

export function BenchPersonaCard({
  persona,
  selected = false,
  disabled = false,
  onToggle,
  onOpenDetail,
  hits = [],
}: BenchPersonaCardProps) {
  const { t } = useI18n();
  const labels = useDimensionLabels();
  const dims = Object.entries(persona.dimensions ?? {}).slice(0, 4);
  const displayName = personaPrimaryName(
    persona.name,
    persona.personaId,
    persona.dimensions ?? {},
  );
  const codename = personaDisplayId(persona.personaId);
  const visibleHits = hits.slice(0, 2);

  return (
    <div
      role={onToggle ? "button" : undefined}
      tabIndex={onToggle && !disabled ? 0 : undefined}
      onClick={onToggle && !disabled ? onToggle : undefined}
      onKeyDown={
        onToggle && !disabled
          ? (event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                onToggle();
              }
            }
          : undefined
      }
      className={`relative flex h-full w-full flex-col overflow-hidden rounded-xl border border-transparent p-4 transition-all duration-200 ${
        onToggle && !disabled ? "cursor-pointer" : ""
      } ${
        selected
          ? "persona-card--selected"
          : disabled
            ? "glass-tile glass-tile--dim opacity-80"
            : "glass-tile glass-tile--hover border-outline/20"
      }`}
    >
      <div className="flex items-start gap-3">
        <div className="relative shrink-0">
          <PersonaAvatar
            personaId={persona.personaId}
            dimensions={persona.dimensions}
            size="md"
          />
          {onToggle ? (
            <span
              className={`absolute -left-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full border shadow-sm ${
                selected
                  ? "border-primary/40 bg-primary/15 text-primary"
                  : "border-outline/50 bg-surface-lowest/90 text-transparent"
              }`}
              aria-hidden
            >
              <Sym name="check" size={14} />
            </span>
          ) : null}
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            {/* min-w-[5rem], not min-w-0: this block holds the identity, so it
                is the one thing on the card that must never be squeezed away.
                Both lines truncate, so a flex row that hands all the width to
                the chip beside them renders the card with no name and no id --
                which is exactly what a long source value used to do. */}
            <div className="min-w-[7rem] flex-1 text-left">
              <div className="min-w-0">
                <p className="truncate font-display text-[15px] font-semibold leading-tight text-text-main">
                  {displayName}
                </p>
                {/* Truncate like the name above. Short ids ("persona-0042")
                    fit on one line, but a longer one ("persona-vn-drv-001")
                    wraps to four, overflows the header block and pushes the
                    name out of the card entirely. */}
                <p
                  className="mt-1 truncate font-mono text-[11px] tracking-wide text-text-dim"
                  title={codename}
                >
                  {codename}
                </p>
              </div>
            </div>
            {/* The chip yields before the name does: it can shrink to nothing
                and its full value stays available on hover. */}
            <div className="flex min-w-0 shrink items-center gap-1">
              {persona.source ? (
                <ToneChip
                  tone="neutral"
                  muted
                  className={`${CHIP_TEXT_CLASS} min-w-0 max-w-[4.5rem] truncate`}
                  title={persona.source}
                >
                  {persona.source}
                </ToneChip>
              ) : null}
              {onOpenDetail && (
                <button
                  type="button"
                  onClick={(event) => {
                    event.stopPropagation();
                    onOpenDetail();
                  }}
                  aria-label={t("cockpitSetup.persona.viewDetails", {
                    name: displayName,
                  })}
                  className={`rounded-md p-1.5 text-text-dim transition hover:bg-surface-high hover:text-primary ${FOCUS_RING}`}
                >
                  <Sym name="info" size={16} />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {visibleHits.length > 0 ? (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {visibleHits.map((hit) => {
            const hitValue = labels.valueLabel(hit.dimensionId, hit.value);
            return (
              <span
                key={`${hit.dimensionId}:${hit.value}`}
                title={`${labels.dimLabel(hit.dimensionId, hit.label)}: ${hitValue}`}
                className="inline-flex max-w-full items-center gap-1 rounded-full border border-primary/25 bg-primary/10 px-2 py-0.5 text-[11px] font-medium text-primary"
              >
                <span className="opacity-70">
                  {t("cockpitSetup.persona.match")}
                </span>
                <span className="opacity-40">·</span>
                <span className="truncate">{hitValue}</span>
              </span>
            );
          })}
          {hits.length > visibleHits.length ? (
            <span className="self-center text-[11px] text-text-dim">
              +{hits.length - visibleHits.length}
            </span>
          ) : null}
        </div>
      ) : null}

      {dims.length > 0 ? (
        <button
          type="button"
          disabled={disabled}
          onClick={onToggle}
          className={`mt-auto w-full border-t border-outline/20 pt-3 text-left disabled:cursor-default disabled:opacity-80 ${visibleHits.length ? "mt-3" : "mt-4"} ${FOCUS_RING}`}
        >
          <dl className="space-y-2">
            {dims.map(([key, value], index) => {
              const fallback =
                key in DIM_LABEL_KEYS
                  ? t(DIM_LABEL_KEYS[key])
                  : key.replace(/_/g, " ");
              const label = labels.dimLabel(key, fallback);
              const displayValue = labels.valueLabel(key, value);
              return (
                <div
                  key={key}
                  className="grid min-w-0 grid-cols-[4.75rem_1fr] items-baseline gap-x-2"
                >
                  <dt
                    className="truncate text-[11px] text-text-dim"
                    title={label}
                  >
                    <span
                      className={`mr-1.5 inline-block h-1.5 w-1.5 rounded-full align-middle ${dotClass(personaDimChipTone(key, index))}`}
                      aria-hidden
                    />
                    {label}
                  </dt>
                  <dd
                    className="min-w-0 truncate text-[13px] leading-snug text-text-main"
                    title={displayValue}
                  >
                    {displayValue}
                  </dd>
                </div>
              );
            })}
          </dl>
        </button>
      ) : null}
    </div>
  );
}

function dotClass(tone: ReturnType<typeof personaDimChipTone>): string {
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
