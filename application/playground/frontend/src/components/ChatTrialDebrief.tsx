/**
 * Shared chat trial debrief: persona subjective scores, objective task metrics,
 * then the conversational transcript (batch monitor + RunDetail).
 */
import type { ReactNode } from "react";

import { PersonaBubble, RecBotBubble } from "./cockpit/TurnBubble";
import { humanizeToken } from "./cockpit/cockpitShared";
import { useI18n } from "@/i18n/I18nProvider";
import {
  localizedBooleanLabel,
  localizedDecisionLabel,
  localizedStructuredChoiceLabel,
  type Translate,
} from "@/lib/localizedDisplayValues";
import {
  StatTile,
  appName,
  type RunConfig,
  type RunDetailView,
  type RunPersona,
  type RunTranscriptTurn,
} from "./runsShared";
import type { TurnView } from "@/lib/types";
import type { PlaygroundQuestionnaire } from "@/lib/types";
import type {
  TrialEvaluationArtifact,
  TrialEvaluationContext,
  TrialEvaluationFacet,
} from "@/lib/types";
import type { SelfReportSchema, UserFeedbackArtifact } from "@/lib/types";
import { SchemaSelfReportPanel } from "./SchemaSelfReportPanel";

export type ChatTrialVerifier = NonNullable<RunDetailView["verifier"]>;

export interface ChatTrialDebriefBodyProps {
  config: RunConfig;
  transcript: RunTranscriptTurn[];
  persona?: RunPersona | null;
  questionnaire?: PlaygroundQuestionnaire | null;
  userFeedback?: UserFeedbackArtifact | null;
  selfReportSchema?: SelfReportSchema | null;
  metricScores?: RunDetailView["metricScores"];
  verifier?: ChatTrialVerifier | null;
  trialEvaluation?: TrialEvaluationArtifact | null;
  /** Task title — the SUT label when `config.applicationId` is unknown. */
  taskTitle?: string | null;
  /** When false, hide section headings (embedded in batch monitor). */
  showSectionHeadings?: boolean;
}

function DashedNote({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-md glass-tile glass-tile--dim px-4 py-8 text-center text-[15px] text-text-variant">
      {children}
    </div>
  );
}

function SectionHeading({ children }: { children: ReactNode }) {
  return <h2 className="hud text-[12px] text-primary">{children}</h2>;
}

function SubsectionHeading({ children }: { children: ReactNode }) {
  return (
    <h3 className="text-[14px] font-semibold text-text-main">{children}</h3>
  );
}

function previewText(value: string | null | undefined, limit = 180): string {
  const normalized = (value ?? "").trim().replace(/\s+/g, " ");
  if (!normalized) return "";
  if (normalized.length <= limit) return normalized;
  return `${normalized.slice(0, limit - 1).trimEnd()}…`;
}

function contextOfType(
  trialEvaluation: TrialEvaluationArtifact | null | undefined,
  contextType: string,
): TrialEvaluationContext | null {
  return (
    trialEvaluation?.contexts.find(
      (context) => context.contextType === contextType,
    ) ?? null
  );
}

function facetValue(
  context: TrialEvaluationContext | null,
  key: string,
): string | number | boolean | null {
  const facet = context?.facets.find((item) => item.key === key);
  return facet?.value ?? null;
}

function facetText(
  context: TrialEvaluationContext | null,
  key: string,
): string {
  const value = facetValue(context, key);
  return typeof value === "string" ? value : "";
}

function facetNumber(
  context: TrialEvaluationContext | null,
  key: string,
): number | null {
  const value = facetValue(context, key);
  return typeof value === "number" ? value : null;
}

function formatFacetToken(
  value: string | number | boolean | null | undefined,
  t: Translate,
): string {
  if (typeof value === "boolean") return localizedBooleanLabel(value, t);
  if (typeof value === "number") return String(value);
  if (!value) return "-";
  return localizedStructuredChoiceLabel(value, t) ?? humanizeToken(value);
}

function SummarySignalCard({
  title,
  value,
  eyebrow,
  detail,
}: {
  title: string;
  value: ReactNode;
  eyebrow?: string | null;
  detail?: string | null;
}) {
  return (
    <div className="rounded-md glass-panel p-4">
      <div className="flex items-center justify-between gap-2">
        <span className="hud text-[11px] text-text-dim">{title}</span>
        {eyebrow ? (
          <span className="inline-flex items-center glass-tile rounded px-2 py-0.5 text-[12px] text-text-variant">
            {eyebrow}
          </span>
        ) : null}
      </div>
      <div className="mt-2 text-[20px] font-semibold leading-tight text-text-main">
        {value}
      </div>
      {detail ? (
        <p className="mt-2 text-[14px] leading-relaxed text-text-variant">
          {detail}
        </p>
      ) : null}
    </div>
  );
}

function ChatContractSummary({
  trialEvaluation,
}: {
  trialEvaluation: TrialEvaluationArtifact | null | undefined;
}) {
  const { t } = useI18n();
  const outcome = contextOfType(trialEvaluation, "task_outcome");
  const conversation = contextOfType(trialEvaluation, "conversation_summary");
  const feedback =
    contextOfType(trialEvaluation, "user_feedback") ??
    contextOfType(trialEvaluation, "feedback");

  if (!outcome && !conversation && !feedback) return null;

  const outcomeStatus = formatFacetToken(
    facetValue(outcome, "outcome_status"),
    t,
  );
  const resolutionBasis = facetText(outcome, "resolution_basis");
  const outcomeReason = previewText(facetText(outcome, "outcome_reason"), 140);

  // Prose, not a token. formatFacetToken title-cases every word, which reads as
  // nonsense in a language that does not capitalise that way: "Dẫn Tôi Đến
  // Landmark 81 Đi."
  const conversationPath = previewText(
    facetText(conversation, "conversation_path"),
    180,
  );
  const turnCount = facetNumber(conversation, "message_count");
  const clarificationCount = facetNumber(
    conversation,
    "clarification_question_count",
  );
  const processNotes = previewText(
    facetText(conversation, "process_notes"),
    140,
  );

  const rating = facetNumber(feedback, "overall_experience_rating");
  const needSatisfaction = formatFacetToken(
    facetValue(feedback, "need_constraint_satisfaction"),
    t,
  );
  const feedbackReason = previewText(
    facetText(feedback, "feedback_reason"),
    140,
  );

  return (
    <div className="space-y-3 glass-tile rounded-md p-4">
      <div className="space-y-1">
        <SubsectionHeading>{t("runs.trialSummary")}</SubsectionHeading>
        <p className="text-[14px] leading-relaxed text-text-variant">
          {t("runs.trialSummaryDescription")}
        </p>
      </div>
      <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
        {outcome ? (
          <SummarySignalCard
            title={t("runs.taskOutcome")}
            value={outcomeStatus}
            eyebrow={
              resolutionBasis ? formatFacetToken(resolutionBasis, t) : null
            }
            detail={outcomeReason || t("runs.noOutcomeExplanation")}
          />
        ) : null}
        {conversation ? (
          <SummarySignalCard
            title={t("runs.conversationPath")}
            value={conversationPath}
            eyebrow={
              turnCount != null || clarificationCount != null
                ? t("runs.messagesAndClarifications", {
                    messages: turnCount ?? "-",
                    clarifications: clarificationCount ?? "-",
                  })
                : null
            }
            detail={processNotes || t("runs.noProcessSummary")}
          />
        ) : null}
        {feedback ? (
          <SummarySignalCard
            title={t("runs.userFeedback")}
            value={rating != null ? `${rating}/10` : needSatisfaction}
            eyebrow={rating != null ? needSatisfaction : null}
            detail={feedbackReason || t("runs.noFeedbackExplanation")}
          />
        ) : null}
      </div>
    </div>
  );
}

// Facets the summary cards already render whole. Repeating a value the reader
// just looked at is not detail, it is noise.
const SUMMARY_FACET_KEYS = new Set([
  "outcome_status",
  "resolution_basis",
  "message_count",
  "turn_count",
  "clarification_question_count",
  "overall_experience_rating",
  "need_constraint_satisfaction",
]);

// Where each card takes its prose from, and how much of it the card shows.
// Repeating a facet whose card lost only a clause is not detail; repeating the
// conversation path, of which the card shows a fifth, is the whole point.
const CARD_PROSE_LIMITS: Record<string, number> = {
  outcome_reason: 140,
  process_notes: 140,
  feedback_reason: 140,
  conversation_path: 180,
};
// A card is "close enough to complete" until the full text is half again as
// long as what it showed.
const WORTH_REPEATING = 1.5;

// Above this, a string is a sentence worth checking for repetition. At or
// below, it is a label and two facets may share one by coincidence.
const PROSE_MIN_LENGTH = 60;

// Facets that restate one another. The value is the facet that survives: the
// one a reader can act on without decoding it.
const SUPERSEDED_BY: Record<string, string> = {
  decision_match: "decision_correct",
  tool_call_match: "tool_calls_correct",
  observed_tools: "tool_call_report",
};

/** Facets worth showing again, per context. Exported for tests. */
export function newFacetsIn(
  context: TrialEvaluationContext,
  present: ReadonlySet<string>,
  seenProse: Set<string>,
): TrialEvaluationFacet[] {
  const kept: TrialEvaluationFacet[] = [];
  for (const facet of context.facets ?? []) {
    if (isBlankFacet(facet.value)) continue;
    if (SUMMARY_FACET_KEYS.has(facet.key)) continue;
    // "control" is how a task marks the metadata it slices reports by --
    // case_type, group, error_type, input_constraint. It belongs in the CSV
    // and the cohort breakdowns; on this page it is eight rows of codes
    // restating what the process note already says in a sentence.
    if (facet.role === "control") continue;
    // Two spellings of one verdict: "mismatch" and "no" say the same thing,
    // and a name list is already inside the call report.
    const winner = SUPERSEDED_BY[facet.key];
    if (winner && present.has(winner)) continue;

    if (typeof facet.value === "string") {
      const text = facet.value.trim();
      const shown = CARD_PROSE_LIMITS[facet.key];
      if (shown != null && text.length <= shown * WORTH_REPEATING) continue;
      // Deduplicate prose only. Short values are labels, not paragraphs, and
      // several of them legitimately read the same: "decision correct: no" and
      // "tool calls correct: no" are two answers that happen to share a word.
      if (text.length > PROSE_MIN_LENGTH) {
        // A verdict derived from the persona's own words repeats them
        // verbatim: outcome_reason and feedback_reason are the same paragraph
        // whenever resolution_basis is user_feedback.
        const fingerprint = text.slice(0, 120);
        if (seenProse.has(fingerprint)) continue;
        seenProse.add(fingerprint);
      }
    }
    kept.push(facet);
  }
  return kept;
}

/**
 * What the verifier recorded that the rest of the page has not already said.
 *
 * Not everything it recorded: the summary cards above show the headline facets
 * in full, and repeating them here made a reader scan the same sentence three
 * times before reaching anything new. So each facet is dropped when it is
 * already legible somewhere else, and a context with nothing left disappears.
 *
 * Labels come from the task's own payload rather than a lookup here, so a task
 * that adds a facet gets it rendered without touching this file.
 */
function EvaluationDetail({
  trialEvaluation,
}: {
  trialEvaluation: TrialEvaluationArtifact | null | undefined;
}) {
  const { t } = useI18n();
  const all = trialEvaluation?.contexts ?? [];
  // Superseding crosses contexts: decision_match sits in the task's own
  // diagnostic block while the verdict it duplicates sits in task_outcome.
  const present = new Set(
    all.flatMap((context) =>
      (context.facets ?? [])
        .filter((facet) => !isBlankFacet(facet.value))
        .map((facet) => facet.key),
    ),
  );
  const seenProse = new Set<string>();
  const contexts = all
    .map((context) => ({
      ...context,
      facets: newFacetsIn(context, present, seenProse),
    }))
    .filter((context) => context.facets.length > 0);
  if (contexts.length === 0) return null;

  return (
    <div className="space-y-3 glass-tile rounded-md p-4">
      <div className="space-y-1">
        <SubsectionHeading>{t("runs.evaluationDetail")}</SubsectionHeading>
        <p className="text-[14px] leading-relaxed text-text-variant">
          {t("runs.evaluationDetailDescription")}
        </p>
      </div>
      {contexts.map((context) => (
        <EvaluationContextBlock key={context.key} context={context} t={t} />
      ))}
    </div>
  );
}

function isBlankFacet(value: string | number | boolean | null | undefined) {
  return value === null || value === undefined || value === "";
}

/** Prose facets get their own paragraph; short values line up as a chip grid. */
function EvaluationContextBlock({
  context,
  t,
}: {
  context: TrialEvaluationContext;
  t: Translate;
}) {
  const facets = context.facets ?? [];
  const prose = facets.filter(
    (facet) => typeof facet.value === "string" && facet.value.trim().length > 60,
  );
  const compact = facets.filter((facet) => !prose.includes(facet));

  return (
    <div className="rounded-md glass-panel p-4">
      <div className="hud text-[11px] text-text-dim">
        {localizedContextLabel(context, t)}
      </div>
      {compact.length > 0 ? (
        <dl className="mt-3 grid grid-cols-1 gap-x-6 gap-y-2 sm:grid-cols-2">
          {compact.map((facet) => (
            <div
              key={facet.key}
              className="flex items-baseline justify-between gap-3 border-b border-text-dim/10 pb-1.5"
            >
              <dt className="text-[13px] text-text-dim">{facet.label}</dt>
              <dd className="text-right text-[14px] font-medium text-text-main">
                {typeof facet.value === "string" && facet.kind === "textual"
                  ? facet.value
                  : formatFacetToken(facet.value, t)}
              </dd>
            </div>
          ))}
        </dl>
      ) : null}
      {prose.map((facet) => (
        <div key={facet.key} className="mt-3">
          <div className="text-[13px] text-text-dim">{facet.label}</div>
          {/* whitespace-pre-line: a turn-by-turn path is written one turn per
              line, and collapsing it into a paragraph makes it unreadable. */}
          <p className="mt-1 whitespace-pre-line text-[14px] leading-relaxed text-text-variant">
            {String(facet.value)}
          </p>
        </div>
      ))}
    </div>
  );
}

/** A known context type gets a translated heading; anything else keeps its own. */
function localizedContextLabel(
  context: TrialEvaluationContext,
  t: Translate,
): string {
  switch (context.contextType) {
    case "task_outcome":
      return t("runs.taskOutcome");
    case "conversation_summary":
      return t("runs.conversationPath");
    case "user_feedback":
      return t("runs.userFeedback");
    default:
      return context.label || humanizeToken(context.contextType ?? context.key);
  }
}

const _DEFAULT_FEEDBACK_KEYS = new Set([
  "needConstraintSatisfaction",
  "personalPreferenceSatisfaction",
  "overallExperienceRating",
  "reason",
  "askedUsefulClarificationQuestions",
  "clarifyingNotes",
  "trustLevel",
  "feltUnderstood",
]);

function inferSchemaFromFeedback(
  feedback: UserFeedbackArtifact,
): SelfReportSchema {
  const fields: SelfReportSchema["fields"] = [];
  for (const [key, value] of Object.entries(feedback)) {
    if (value === null || value === undefined || value === "") continue;
    let kind = "string";
    let minimum: number | null = null;
    let maximum: number | null = null;
    if (typeof value === "boolean") kind = "boolean";
    else if (typeof value === "number") {
      kind = "integer";
      if (key === "overallExperienceRating" || /rating|score/i.test(key)) {
        minimum = 1;
        maximum = 10;
      }
    } else if (
      typeof value === "string" &&
      ["yes", "no", "partially", "unsure", "true", "false"].includes(
        value.trim().toLowerCase(),
      )
    ) {
      kind = "enum";
    }
    fields.push({
      key,
      prompt: humanizeToken(key),
      kind,
      minimum,
      maximum,
      explains:
        key === "reason"
          ? "overallExperienceRating"
          : key === "clarifyingNotes"
            ? "askedUsefulClarificationQuestions"
            : null,
    });
  }
  const rank = (key: string) => {
    if (key === "overallExperienceRating") return 0;
    if (key === "reason") return 1;
    if (_DEFAULT_FEEDBACK_KEYS.has(key)) return 2;
    return 3;
  };
  fields.sort(
    (a, b) => rank(a.key) - rank(b.key) || a.key.localeCompare(b.key),
  );
  return { fields };
}

/** Persona simulator self-report after the chat (from ``user_feedback.json``). */
export function ChatSelfReport({
  questionnaire,
  userFeedback,
  selfReportSchema,
}: {
  questionnaire: PlaygroundQuestionnaire | null | undefined;
  userFeedback?: UserFeedbackArtifact | null;
  selfReportSchema?: SelfReportSchema | null;
}) {
  const { rich } = useI18n();
  const feedback: UserFeedbackArtifact | null =
    userFeedback && Object.keys(userFeedback).length > 0
      ? userFeedback
      : questionnaire
        ? ({
            overallExperienceRating: questionnaire.overallRating,
            reason: questionnaire.ratingReason,
            needConstraintSatisfaction:
              (questionnaire.constraintSatisfaction ?? 0) > 0
                ? questionnaire.constraintSatisfaction >= 4
                  ? "yes"
                  : questionnaire.constraintSatisfaction >= 3
                    ? "partially"
                    : "no"
                : undefined,
            personalPreferenceSatisfaction:
              (questionnaire.preferenceSatisfaction ?? 0) > 0
                ? questionnaire.preferenceSatisfaction >= 4
                  ? "yes"
                  : questionnaire.preferenceSatisfaction >= 3
                    ? "partially"
                    : "no"
                : undefined,
            askedUsefulClarificationQuestions:
              questionnaire.askedUsefulClarifyingQuestions,
            clarifyingNotes: questionnaire.clarifyingNotes,
            ...Object.fromEntries(
              Object.entries(questionnaire).filter(
                ([key]) =>
                  ![
                    "overallRating",
                    "ratingReason",
                    "constraintSatisfaction",
                    "constraintRationale",
                    "preferenceSatisfaction",
                    "preferenceRationale",
                    "askedUsefulClarifyingQuestions",
                    "clarifyingNotes",
                  ].includes(key),
              ),
            ),
          } as UserFeedbackArtifact)
        : null;

  const schema = selfReportSchema?.fields?.length
    ? selfReportSchema
    : feedback
      ? inferSchemaFromFeedback(feedback)
      : null;

  if (schema?.fields?.length && feedback) {
    return <SchemaSelfReportPanel schema={schema} feedback={feedback} />;
  }

  return (
    <DashedNote>
      {rich("runs.noPersonaSelfReport", {
        path: (parts) => (
          <span className="font-mono text-[13px]">{parts}</span>
        ),
      })}
    </DashedNote>
  );
}

/** Run completeness strip — shown first so pass/fail is visible before quality insights. */
export function ChatObjectiveEvaluation({
  metrics,
  verifier,
}: {
  metrics: RunDetailView["metricScores"];
  verifier?: ChatTrialVerifier | null;
}) {
  const { t } = useI18n();
  const artifactMissing =
    verifier &&
    !verifier.passed &&
    (verifier.detail?.includes("transcript.json is missing") ||
      verifier.detail?.includes("artifacts/app/output"));

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        <StatTile caption={t("runs.turns")} value={metrics?.numTurns ?? "-"} />
        {verifier ? (
          <div
            className={`flex flex-col justify-center rounded-lg px-3 py-2.5 ${
              verifier.passed ? "bg-secondary/10" : "bg-danger/10"
            }`}
          >
            <span className="hud text-[11px] text-text-dim">
              {t("runs.runComplete")}
            </span>
            <div className="mt-1 flex items-center gap-2">
              <span className="text-[15px] font-semibold text-text-main">
                {verifier.passed
                  ? t("runs.passedChecks")
                  : t("runs.failedChecks")}
              </span>
              <span className="font-mono text-[13px] text-text-variant">
                {t("runs.reward", { reward: verifier.reward })}
              </span>
            </div>
          </div>
        ) : (
          <div className="flex flex-col justify-center rounded-lg glass-tile glass-tile--dim px-3 py-2.5">
            <span className="hud text-[11px] text-text-dim">
              {t("runs.runComplete")}
            </span>
            <span className="mt-1 text-[15px] text-text-variant">
              {t("runs.checksPending")}
            </span>
          </div>
        )}
      </div>
      {artifactMissing ? (
        <p className="text-[14px] leading-relaxed text-text-variant">
          {t("runs.artifactMissingDescription")}
        </p>
      ) : null}
      {verifier?.detail && !verifier.passed ? (
        <pre className="custom-scrollbar max-h-24 overflow-auto whitespace-pre-wrap rounded-md glass-tile px-3 py-2 font-mono text-[12px] leading-snug text-text-variant">
          {verifier.detail}
        </pre>
      ) : null}
    </div>
  );
}

export function ChatTrialTranscript({
  transcript,
  appLabel,
  domain = "movie",
  persona,
}: {
  transcript: RunTranscriptTurn[];
  appLabel: string;
  domain?: string;
  persona?: RunPersona | null;
}) {
  const { t } = useI18n();
  if (transcript.length === 0) {
    return <DashedNote>{t("runs.noConversationTurns")}</DashedNote>;
  }
  return (
    <div className="space-y-7 rounded-md glass-panel p-5">
      {transcript.map((turn, i) => (
        <TranscriptTurn
          key={turn.turnIndex ?? i}
          turn={turn}
          index={i}
          appLabel={appLabel}
          domain={domain}
          persona={persona}
        />
      ))}
    </div>
  );
}

/** Run checks first, then evaluation (chat summary + persona report), transcript below. */
export function ChatTrialDebriefBody({
  config,
  transcript,
  persona,
  questionnaire,
  userFeedback,
  selfReportSchema,
  metricScores,
  verifier,
  trialEvaluation,
  taskTitle,
  showSectionHeadings = true,
}: ChatTrialDebriefBodyProps) {
  const { t } = useI18n();
  const applicationId = config.applicationId?.trim() || null;
  const app = applicationId
    ? appName(applicationId, t)
    : taskTitle?.trim() || appName(null, t);

  return (
    <div className="space-y-6">
      <section className="space-y-4">
        {showSectionHeadings && (
          <SectionHeading>{t("runs.evaluation")}</SectionHeading>
        )}
        <div className="space-y-2 glass-tile rounded-md p-3">
          <p className="text-[14px] leading-relaxed text-text-variant">
            {t("runs.evaluationDescription")}
          </p>
          <ChatObjectiveEvaluation metrics={metricScores} verifier={verifier} />
        </div>
        <ChatContractSummary trialEvaluation={trialEvaluation} />
        <EvaluationDetail trialEvaluation={trialEvaluation} />
        <div className="space-y-3 glass-tile rounded-md p-4">
          {showSectionHeadings && (
            <SubsectionHeading>{t("runs.personaSelfReport")}</SubsectionHeading>
          )}
          <p className="text-[14px] leading-relaxed text-text-variant">
            {t("runs.personaSelfReportDescription")}
          </p>
          <ChatSelfReport
            questionnaire={questionnaire}
            userFeedback={userFeedback}
            selfReportSchema={selfReportSchema}
          />
        </div>
      </section>

      <section className="space-y-3">
        {showSectionHeadings && (
          <SectionHeading>{t("runs.conversation")}</SectionHeading>
        )}
        <ChatTrialTranscript
          transcript={transcript}
          appLabel={app}
          domain={String(config.domain ?? "movie")}
          persona={persona}
        />
      </section>
    </div>
  );
}

function TranscriptTurn({
  turn,
  index,
  appLabel,
  domain,
  persona,
}: {
  turn: RunTranscriptTurn;
  index: number;
  appLabel: string;
  domain: string;
  persona?: RunPersona | null;
}) {
  const { t } = useI18n();
  const turnView: TurnView = {
    userMessage: turn.userMessage,
    assistantMessage: turn.assistantMessage ?? "",
    structuredExposure: turn.structuredExposure ?? [],
    durationSeconds: turn.durationSeconds,
    plan: [],
  };

  return (
    <div
      className="space-y-7 rise-in"
      style={{
        animationDelay: `${Math.min(index, 6) * 30}ms`,
        animationFillMode: "backwards",
      }}
    >
      <div className="flex items-center justify-center">
        <span className="hud text-[11px] text-text-dim">
          {t("runs.turn", { count: index + 1 })}
        </span>
      </div>
      <PersonaBubble
        message={turn.userMessage}
        personaId={persona?.id}
        personaName={persona?.name}
        personaDimensions={persona?.dimensions ?? undefined}
      />
      {turn.decision && turn.decision !== "continue" ? (
        <div className="flex items-start gap-2.5 pr-10">
          <div className="h-8 w-8 shrink-0" aria-hidden />
          <DecisionTag decision={turn.decision} />
        </div>
      ) : null}
      <RecBotBubble
        turn={turnView}
        domain={domain}
        appName={appLabel}
        foldOpen={false}
        onToggleFold={() => undefined}
      />
    </div>
  );
}

function DecisionTag({ decision }: { decision: string }) {
  const { t } = useI18n();
  const satisfied = decision === "satisfied";
  const cls = satisfied
    ? "text-secondary bg-secondary/10"
    : "text-warn bg-warn/10";
  const label = localizedDecisionLabel(decision, t) ?? humanizeToken(decision);
  return (
    <span
      className={`inline-flex items-center rounded px-1.5 py-px hud text-[11px] ${cls}`}
    >
      {label}
    </span>
  );
}

export default ChatTrialDebriefBody;
