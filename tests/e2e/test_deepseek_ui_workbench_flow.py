"""DeepSeek V4 Pro UI workbench demo-flow smoke test.

This is an opt-in Playwright e2e test. It verifies the downgraded Canvas
branch is not promoted by the four-page DeepSeek UI workbench, then drives the
actual browser route from requirements intake through sandbox review and back
to logic revision. Model endpoints are fulfilled locally so the demo acceptance
does not depend on live DeepSeek credentials.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterator

import pytest

from well_harness.requirements_intake.logic_builder import _build_l1_l4_circuit_view

pytestmark = pytest.mark.e2e

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import expect, sync_playwright  # noqa: E402

ARTIFACT_DIR = Path("artifacts/deepseek-ui-workbench-e2e")
PRIMARY_FLOW = "deepseek-v4-pro-ui-workbench"
CANVAS_STATUS = "degraded-backup"


def _show_logic_builder_workbench(page: Any) -> None:
    page.evaluate(
        """() => {
          document.body.dataset.logicInteractionMode = "workbench";
          const shell = document.querySelector("main.logic-shell");
          if (shell) shell.dataset.workbenchInputModel = "workbench";
        }"""
    )
    expect(page.locator("body")).to_have_attribute("data-logic-interaction-mode", "workbench")


def _expect_trace_consistency(
    locator: Any,
    *,
    state: str,
    consistency_id: str | None = None,
    current_id: str | None = None,
    selected_id: str | None = None,
    selected_source: str | None = None,
    cue: str | None = None,
    cue_label: str | None = None,
    alignable: bool | None = None,
    align_target_id: str | None = None,
    align_source: str | None = None,
) -> None:
    expect(locator).to_have_attribute("data-trace-consistency-state", state)
    if consistency_id is not None:
        expect(locator).to_have_attribute("data-trace-consistency-id", consistency_id)
    if current_id is not None:
        expect(locator).to_have_attribute("data-trace-consistency-current-id", current_id)
        expect(locator).to_have_attribute("data-trace-consistency-current-segment-id", current_id)
    if selected_id is not None:
        expect(locator).to_have_attribute("data-trace-consistency-selected-id", selected_id)
        expect(locator).to_have_attribute("data-trace-consistency-selected-canvas-trace-id", selected_id)
    if selected_source is not None:
        expect(locator).to_have_attribute("data-trace-consistency-selected-source", selected_source)
    if cue is not None:
        expect(locator).to_have_attribute("data-trace-consistency-cue", cue)
    if cue_label is not None:
        expect(locator).to_have_attribute("data-trace-consistency-cue-label", cue_label)
    if alignable is not None:
        expect(locator).to_have_attribute("data-trace-consistency-alignable", "true" if alignable else "false")
    if align_target_id is not None:
        expect(locator).to_have_attribute("data-trace-consistency-align-target-id", align_target_id)
    if align_source is not None:
        expect(locator).to_have_attribute("data-trace-consistency-align-source", align_source)


def _assert_current_segment_consistency_cue_layout(page: Any, *, align_visible: bool) -> None:
    assert page.evaluate(
        """(alignVisible) => {
          const cell = document.querySelector("#logic-current-segment-consistency");
          const cue = document.querySelector("#logic-current-segment-consistency-cue");
          const text = document.querySelector("#logic-current-segment-consistency-text");
          const align = document.querySelector("#logic-current-segment-consistency-align");
          const canvas = document.querySelector("#logic-canvas");
          if (!cell || !cue || !text || !canvas) return false;
          const cellBox = cell.getBoundingClientRect();
          const cueBox = cue.getBoundingClientRect();
          const cueStyle = window.getComputedStyle(cue);
          const cueRects = Array.from(cue.getClientRects()).filter((rect) => rect.width > 0 && rect.height > 0);
          const canvasBox = canvas.getBoundingClientRect();
          const canvasStyle = window.getComputedStyle(canvas);
          const cueInsideCell = cueBox.left >= cellBox.left - 1
            && cueBox.right <= cellBox.right + 1
            && cueBox.top >= cellBox.top - 1
            && cueBox.bottom <= cellBox.bottom + 1;
          const cueSingleLine = cueRects.length === 1 && cueStyle.whiteSpace === "nowrap";
          const rowDoesNotWrap = cell.scrollHeight <= cell.clientHeight + 2;
          const canvasRemainsVisible = canvasBox.width > 0
            && canvasBox.height > 0
            && canvasStyle.display !== "none"
            && canvasStyle.visibility !== "hidden";
          if (!cueInsideCell || !cueSingleLine || !rowDoesNotWrap || !canvasRemainsVisible) return false;
          if (!alignVisible) return true;
          if (!align || align.hidden) return false;
          const alignStyle = window.getComputedStyle(align);
          if (alignStyle.display === "none" || alignStyle.visibility === "hidden") return false;
          const alignBox = align.getBoundingClientRect();
          return !(cueBox.left < alignBox.right
            && cueBox.right > alignBox.left
            && cueBox.top < alignBox.bottom
            && cueBox.bottom > alignBox.top);
        }""",
        align_visible,
    ) is True


def _assert_current_segment_trust_chain_layout(page: Any) -> None:
    layout = page.evaluate(
        """() => {
          const card = document.querySelector("#logic-current-segment-evidence");
          const chain = document.querySelector("#logic-current-segment-trust-chain");
          const globalReview = document.querySelector("#logic-current-segment-global-review");
          const jumps = document.querySelector("#logic-current-segment-anchor-jumps");
          const canvas = document.querySelector("#logic-canvas");
          if (!card || !chain || !globalReview || !jumps || !canvas) return { ok: false, missing: true };
          const bridgeToken = "当前段到全局矩阵";
          const buildCountAudit = (visibleCounts, dataCounts, countsMatch, countsSource) => ({
            visibleCounts,
            dataCounts,
            countsMatch,
            countsSource,
          });
          const buildBridgeAudit = ({ visibleHasBridge, titleHasBridge, ariaHasBridge, scope, expectedScope, visibleHasGlobalMarker = null }) => ({
            token: bridgeToken,
            visibleHasBridge,
            visibleHasGlobalMarker,
            titleHasBridge,
            ariaHasBridge,
            scope,
            expectedScope,
            scopeMatch: scope === expectedScope,
          });
          const cardBox = card.getBoundingClientRect();
          const chainBox = chain.getBoundingClientRect();
          const globalReviewBox = globalReview.getBoundingClientRect();
          const jumpsBox = jumps.getBoundingClientRect();
          const canvasBox = canvas.getBoundingClientRect();
          const chainInsideCard = card.contains(chain)
            && card.contains(jumps)
            && chainBox.left >= cardBox.left - 1
            && chainBox.right <= cardBox.right + 1;
          const chainIntersectsVisibleCard = Math.min(chainBox.bottom, cardBox.bottom)
            - Math.max(chainBox.top, cardBox.top) > 0;
          const chainDoesNotCoverJumps = !(chainBox.left < jumpsBox.right
            && chainBox.right > jumpsBox.left
            && chainBox.top < jumpsBox.bottom
            && chainBox.bottom > jumpsBox.top);
          const jumpsRemainVisible = jumpsBox.width > 0
            && jumpsBox.height > 0
            && jumpsBox.top >= chainBox.top;
          const globalReviewInsideChain = chain.contains(globalReview)
            && globalReviewBox.left >= chainBox.left - 1
            && globalReviewBox.right <= chainBox.right + 1
            && globalReviewBox.top >= chainBox.top - 1
            && globalReviewBox.bottom <= chainBox.bottom + 1;
          const globalReviewText = globalReview.textContent || "";
          const globalReviewTitle = globalReview.getAttribute("title") || "";
          const globalReviewAriaLabel = globalReview.getAttribute("aria-label") || "";
          const globalReviewScope = globalReview.dataset.globalReviewScope || "";
          const globalReviewState = globalReview.dataset.globalReviewState || "";
          const globalReviewHasBridge = globalReviewText.includes(bridgeToken);
          const globalReviewTitleHasBridge = globalReviewTitle.includes(bridgeToken);
          const globalReviewAriaHasBridge = globalReviewAriaLabel.includes(bridgeToken);
          const chainOutputCount = chain.dataset.outputCount || "";
          const chainReviewAnchorCount = chain.dataset.reviewAnchorCount || "";
          const globalReviewOutputCount = globalReview.dataset.outputCount || "";
          const globalReviewAnchorCount = globalReview.dataset.reviewAnchorCount || "";
          const globalReviewCountsMatch = globalReviewOutputCount === chainOutputCount
            && globalReviewAnchorCount === chainReviewAnchorCount
            && globalReviewText.includes(`${globalReviewOutputCount} 输出`)
            && globalReviewText.includes(`${globalReviewAnchorCount} 复核`);
          const globalReviewCountAudit = buildCountAudit(
            { output: globalReviewOutputCount, reviewAnchor: globalReviewAnchorCount },
            { output: chainOutputCount, reviewAnchor: chainReviewAnchorCount },
            globalReviewCountsMatch,
            "left-global-review",
          );
          const globalReviewBridgeAudit = buildBridgeAudit({
            visibleHasBridge: globalReviewHasBridge,
            titleHasBridge: globalReviewTitleHasBridge,
            ariaHasBridge: globalReviewAriaHasBridge,
            scope: globalReviewScope,
            expectedScope: "current-segment-to-global",
          });
          const globalReviewReadable = globalReviewBox.width > 0
            && globalReviewBox.height > 0
            && globalReviewText.includes("全局")
            && globalReviewText.includes("复核")
            && globalReviewText.includes("当前段")
            && globalReviewHasBridge
            && globalReviewScope === "current-segment-to-global"
            && globalReviewCountsMatch;
          const chainTitle = chain.getAttribute("title") || "";
          const chainAriaLabel = chain.getAttribute("aria-label") || "";
          const titleHasCurrentSegment = chainTitle.includes("当前段");
          const titleHasLink = chainTitle.includes("链路");
          const chainTitleHasBridge = chainTitle.includes(bridgeToken);
          const ariaHasCurrentSegment = chainAriaLabel.includes("当前段");
          const ariaHasLink = chainAriaLabel.includes("链路");
          const chainAriaHasBridge = chainAriaLabel.includes(bridgeToken);
          const chainScope = chain.dataset.currentSegmentTrustChainScope || "";
          const expectedChainScope = "current-segment";
          const scopeIsCurrentSegment = chainScope === expectedChainScope;
          const chainAccessible = titleHasCurrentSegment
            && titleHasLink
            && chainTitleHasBridge
            && ariaHasCurrentSegment
            && ariaHasLink
            && chainAriaHasBridge
            && scopeIsCurrentSegment;
          const canvasRemainsVisible = canvasBox.width > 0 && canvasBox.height > 0 && chainAccessible;
          const steps = Array.from(chain.querySelectorAll("[data-trust-chain-step]"));
          const stepsStayInside = steps.length === 4 && steps.every((step) => {
            const stepBox = step.getBoundingClientRect();
            const labels = Array.from(step.querySelectorAll("span, strong, small"));
            const labelsClipSafely = labels.length === 3 && labels.every((label) => {
              const style = window.getComputedStyle(label);
              return style.whiteSpace === "nowrap"
                && style.overflowX === "hidden"
                && style.textOverflow === "ellipsis";
            });
            return stepBox.width > 0
              && stepBox.height > 0
              && stepBox.left >= chainBox.left - 1
              && stepBox.right <= chainBox.right + 1
              && stepBox.top >= chainBox.top - 1
              && labelsClipSafely;
          });
          const ok = chainInsideCard
            && chainIntersectsVisibleCard
            && chainDoesNotCoverJumps
            && jumpsRemainVisible
            && canvasRemainsVisible
            && globalReviewInsideChain
            && globalReviewReadable
            && stepsStayInside;
          return {
            ok,
            chainInsideCard,
            chainIntersectsVisibleCard,
            chainDoesNotCoverJumps,
            jumpsRemainVisible,
            canvasRemainsVisible,
            globalReviewInsideChain,
            globalReviewReadable,
            globalReviewText,
            globalReviewTitle,
            globalReviewAriaLabel,
            globalReviewScope,
            globalReviewState,
            bridgeAudit: globalReviewBridgeAudit,
            chainOutputCount,
            chainReviewAnchorCount,
            globalReviewOutputCount,
            globalReviewAnchorCount,
            globalReviewCountsMatch,
            globalReviewCounts: globalReviewCountAudit,
            countAudit: globalReviewCountAudit,
            globalReviewWidth: globalReviewBox.width,
            globalReviewHeight: globalReviewBox.height,
            chainAccessible,
            chainTitle,
            chainAriaLabel,
            chainScope,
            expectedChainScope,
            titleHasCurrentSegment,
            titleHasLink,
            chainTitleHasBridge,
            ariaHasCurrentSegment,
            ariaHasLink,
            chainAriaHasBridge,
            scopeIsCurrentSegment,
            stepsStayInside,
            stepCount: steps.length,
            cardTop: cardBox.top,
            cardBottom: cardBox.bottom,
            chainTop: chainBox.top,
            chainBottom: chainBox.bottom,
            jumpsTop: jumpsBox.top,
            jumpsBottom: jumpsBox.bottom,
          };
        }"""
    )
    assert layout["ok"] is True, layout


def _expect_bridge_token_across_trace_surfaces(page: Any) -> None:
    bridge_state = page.evaluate(
        """() => {
          const token = "当前段到全局矩阵";
          const surfaces = [
            {
              key: "left-chain",
              element: document.querySelector("#logic-current-segment-trust-chain"),
              visibleRequired: false,
              scope: (element) => element.dataset.currentSegmentTrustChainScope || "",
              expectedScope: "current-segment",
            },
            {
              key: "left-global-review",
              element: document.querySelector("#logic-current-segment-global-review"),
              visibleRequired: true,
              scope: (element) => element.dataset.globalReviewScope || "",
              expectedScope: "current-segment-to-global",
            },
            {
              key: "canvas-selected",
              element: document.querySelector("#logic-selected-target-label"),
              visibleRequired: false,
              scope: (element) => element.dataset.canvasTrustChainScope || "",
              expectedScope: "current-segment",
            },
            {
              key: "canvas-source",
              element: document.querySelector("#logic-canvas-source"),
              visibleRequired: false,
              scope: (element) => element.dataset.canvasTrustChainScope || "",
              expectedScope: "current-segment",
            },
            {
              key: "right-context",
              element: document.querySelector("#logic-context-requirement-trace"),
              visibleRequired: false,
              scope: (element) => element.dataset.contextTrustChainScope || "",
              expectedScope: "current-segment",
            },
            {
              key: "right-annotation",
              element: document.querySelector("#logic-annotation-requirement-trace"),
              visibleRequired: false,
              scope: (element) => element.dataset.annotationTrustChainScope || "",
              expectedScope: "current-segment",
            },
          ];
          const checks = surfaces.map(({ key, element, visibleRequired, scope, expectedScope }) => {
            if (!element) return { key, ok: false, reason: "missing-surface" };
            const text = element.textContent || "";
            const title = element.getAttribute("title") || "";
            const ariaLabel = element.getAttribute("aria-label") || "";
            const actualScope = scope(element);
            const visibleHasToken = text.includes(token);
            const titleHasToken = title.includes(token);
            const ariaHasToken = ariaLabel.includes(token);
            const scopeMatch = actualScope === expectedScope;
            const ok = (!visibleRequired || visibleHasToken)
              && titleHasToken
              && ariaHasToken
              && scopeMatch;
            return {
              key,
              ok,
              visibleRequired,
              visibleHasToken,
              titleHasToken,
              ariaHasToken,
              scope: actualScope,
              expectedScope,
              scopeMatch,
              text,
              title,
              ariaLabel,
            };
          });
          return {
            ok: checks.every((check) => check.ok),
            token,
            checks,
          };
        }"""
    )
    assert bridge_state["ok"] is True, bridge_state


def _expect_global_review_counts_across_trace_surfaces(page: Any) -> None:
    count_state = page.evaluate(
        """() => {
          const parseIntOrMissing = (value) => Number.parseInt(String(value ?? "-1"), 10);
          const chain = document.querySelector("#logic-current-segment-trust-chain");
          const globalReview = document.querySelector("#logic-current-segment-global-review");
          const selected = document.querySelector("#logic-selected-target-label");
          const canvasSource = document.querySelector("#logic-canvas-source");
          const context = document.querySelector("#logic-context-requirement-trace");
          const annotation = document.querySelector("#logic-annotation-requirement-trace");
          if (!chain || !globalReview || !selected || !canvasSource || !context || !annotation) {
            return { ok: false, reason: "missing-surface" };
          }
          const expectedCounts = {
            output: parseIntOrMissing(chain.dataset.outputCount),
            reviewAnchor: parseIntOrMissing(chain.dataset.reviewAnchorCount),
          };
          const sameCounts = (counts) => counts.output === expectedCounts.output
            && counts.reviewAnchor === expectedCounts.reviewAnchor;
          const checkDataCounts = (key, element, outputAttr, reviewAttr, expectedScope, scopeValue) => {
            const dataCounts = {
              output: parseIntOrMissing(element.dataset[outputAttr]),
              reviewAnchor: parseIntOrMissing(element.dataset[reviewAttr]),
            };
            return {
              key,
              ok: sameCounts(dataCounts) && scopeValue === expectedScope,
              dataCounts,
              expectedCounts,
              dataCountsMatch: sameCounts(dataCounts),
              visibleCounts: null,
              visibleCountsMatch: null,
              visibleRaw: "",
              scope: scopeValue,
              expectedScope,
              scopeMatch: scopeValue === expectedScope,
            };
          };
          const checkVisibleCounts = (base, visibleRaw, visibleCounts) => ({
            ...base,
            visibleRaw,
            visibleCounts,
            visibleCountsMatch: sameCounts(visibleCounts),
            ok: base.ok && sameCounts(visibleCounts),
          });
          const globalText = globalReview.textContent || "";
          const globalOutput = (globalText.match(/(\\d+)\\s*输出/) || [])[1];
          const globalReviewAnchors = (globalText.match(/(\\d+)\\s*复核/) || [])[1];
          const selectedTail = window.getComputedStyle(selected, "::after").content || "";
          const selectedCounts = selectedTail.match(/段链\\s*(\\d+)\\/(\\d+)全局/) || [];
          const contextTail = window.getComputedStyle(context, "::after").content || "";
          const contextCounts = contextTail.match(/段链\\s*(\\d+)输出\\/(\\d+)全局复核/) || [];
          const annotationTail = window.getComputedStyle(annotation, "::after").content || "";
          const annotationCounts = annotationTail.match(/段链\\s*(\\d+)输出\\/(\\d+)全局复核/) || [];
          const checks = [
            checkVisibleCounts(
              checkDataCounts("left-global-review", globalReview, "outputCount", "reviewAnchorCount", "current-segment-to-global", globalReview.dataset.globalReviewScope || ""),
              globalText,
              { output: parseIntOrMissing(globalOutput), reviewAnchor: parseIntOrMissing(globalReviewAnchors) },
            ),
            checkVisibleCounts(
              checkDataCounts("canvas-selected", selected, "canvasTrustChainOutputCount", "canvasTrustChainReviewAnchorCount", "current-segment", selected.dataset.canvasTrustChainScope || ""),
              selectedTail,
              { output: parseIntOrMissing(selectedCounts[1]), reviewAnchor: parseIntOrMissing(selectedCounts[2]) },
            ),
            checkDataCounts("canvas-source-data", canvasSource, "canvasTrustChainOutputCount", "canvasTrustChainReviewAnchorCount", "current-segment", canvasSource.dataset.canvasTrustChainScope || ""),
            checkVisibleCounts(
              checkDataCounts("right-context", context, "contextTrustChainOutputCount", "contextTrustChainReviewAnchorCount", "current-segment", context.dataset.contextTrustChainScope || ""),
              contextTail,
              { output: parseIntOrMissing(contextCounts[1]), reviewAnchor: parseIntOrMissing(contextCounts[2]) },
            ),
            checkVisibleCounts(
              checkDataCounts("right-annotation", annotation, "annotationTrustChainOutputCount", "annotationTrustChainReviewAnchorCount", "current-segment", annotation.dataset.annotationTrustChainScope || ""),
              annotationTail,
              { output: parseIntOrMissing(annotationCounts[1]), reviewAnchor: parseIntOrMissing(annotationCounts[2]) },
            ),
          ];
          return {
            ok: expectedCounts.output > 0
              && expectedCounts.reviewAnchor > 0
              && checks.every((check) => check.ok),
            expectedCounts,
            checks,
          };
        }"""
    )
    assert count_state["ok"] is True, count_state


def _assert_layout_target_uncovered(page: Any, selector: str) -> None:
    assert page.evaluate(
        """(targetSelector) => {
          const target = document.querySelector(targetSelector);
          if (!target) return false;
          const box = target.getBoundingClientRect();
          if (box.width <= 0 || box.height <= 0) return false;
          const targetStyle = window.getComputedStyle(target);
          const targetIsVisible = targetStyle.display !== "none"
            && targetStyle.visibility !== "hidden"
            && Number(targetStyle.opacity || "1") > 0;
          if (!targetIsVisible) return false;
          const x = box.left + box.width / 2;
          const y = box.top + box.height / 2;
          if (x < 0 || y < 0 || x > window.innerWidth || y > window.innerHeight) return false;
          if (targetStyle.pointerEvents === "none") return true;
          const hit = document.elementFromPoint(x, y);
          return Boolean(hit && (hit === target || target.contains(hit) || hit.closest(targetSelector) === target));
        }""",
        selector,
    ) is True


def _expect_trust_review_consistency(
    locator: Any,
    *,
    state: str,
    review_id: str | None = None,
    current_id: str | None = None,
    selected_id: str | None = None,
) -> None:
    expect(locator).to_have_attribute("data-trace-consistency-review-state", state)
    if review_id is not None:
        expect(locator).to_have_attribute("data-trace-consistency-review-id", review_id)
    if current_id is not None:
        expect(locator).to_have_attribute("data-trace-consistency-review-current-id", current_id)
        expect(locator).to_have_attribute("data-trace-consistency-review-current-segment-id", current_id)
    if selected_id is not None:
        expect(locator).to_have_attribute("data-trace-consistency-review-selected-id", selected_id)
        expect(locator).to_have_attribute("data-trace-consistency-review-selected-canvas-trace-id", selected_id)


def _expect_trust_spine_consistency(
    locator: Any,
    *,
    state: str,
    current_id: str | None = None,
    selected_id: str | None = None,
    selected_source: str | None = None,
) -> None:
    expect(locator).to_have_attribute("data-trace-consistency-state", state)
    expect(locator).to_have_attribute("data-trace-consistency-review-state", state)
    if current_id is not None:
        expect(locator).to_have_attribute("data-trace-consistency-current-segment-id", current_id)
        expect(locator).to_have_attribute("data-trace-consistency-review-current-segment-id", current_id)
    if selected_id is not None:
        expect(locator).to_have_attribute("data-trace-consistency-selected-canvas-trace-id", selected_id)
        expect(locator).to_have_attribute("data-trace-consistency-review-selected-canvas-trace-id", selected_id)
    if selected_source is not None:
        expect(locator).to_have_attribute("data-trace-consistency-selected-source", selected_source)
        expect(locator).to_have_attribute("data-trace-consistency-review-selected-source", selected_source)


def _expect_requirement_trace_audit(
    locator: Any,
    *,
    prefix: str,
    state: str | None = None,
    trace_id: str | None = None,
    current_id: str | None = None,
    selected_id: str | None = None,
    selected_source: str | None = None,
) -> None:
    if state is not None:
        expect(locator).to_have_attribute(f"data-{prefix}-trace-consistency-state", state)
    if trace_id is not None:
        expect(locator).to_have_attribute(f"data-{prefix}-requirement-trace-id", trace_id)
    if current_id is not None:
        expect(locator).to_have_attribute(f"data-{prefix}-trace-consistency-current-segment-id", current_id)
        expect(locator).to_have_attribute(f"data-{prefix}-requirement-trace-current-segment-id", current_id)
    if selected_id is not None:
        expect(locator).to_have_attribute(f"data-{prefix}-trace-consistency-selected-canvas-trace-id", selected_id)
        expect(locator).to_have_attribute(f"data-{prefix}-requirement-trace-selected-canvas-trace-id", selected_id)
    if selected_source is not None:
        expect(locator).to_have_attribute(f"data-{prefix}-requirement-trace-selected-source", selected_source)


def _expect_current_segment_trust_chain_mirror(page: Any, *, expected_trace_id: str | None = None) -> None:
    mirror_state = page.evaluate(
        """(expectedTraceId) => {
          const chain = document.querySelector("#logic-current-segment-trust-chain");
          const context = document.querySelector("#logic-context-requirement-trace");
          const annotation = document.querySelector("#logic-annotation-requirement-trace");
          const selected = document.querySelector("#logic-selected-target-label");
          const source = document.querySelector("#logic-canvas-source");
          if (!chain || !context || !annotation || !selected || !source) {
            return { ok: false, reason: "missing-surface" };
          }
          const left = {
            state: chain.dataset.currentSegmentTrustChain || "",
            traceId: chain.dataset.currentSegmentTraceId || "",
            sourceAnchorId: chain.dataset.sourceAnchorId || "",
            nodeCount: chain.dataset.nodeCount || "",
            wireCount: chain.dataset.wireCount || "",
            outputCount: chain.dataset.outputCount || "",
            reviewAnchorCount: chain.dataset.reviewAnchorCount || "",
            scope: chain.dataset.currentSegmentTrustChainScope || "",
          };
          const target = (element, prefix) => ({
            state: element.dataset[`${prefix}TrustChainState`] || "",
            traceId: element.dataset[`${prefix}TrustChainTraceId`] || "",
            sourceAnchorId: element.dataset[`${prefix}TrustChainSourceAnchorId`] || "",
            nodeCount: element.dataset[`${prefix}TrustChainNodeCount`] || "",
            wireCount: element.dataset[`${prefix}TrustChainWireCount`] || "",
            outputCount: element.dataset[`${prefix}TrustChainOutputCount`] || "",
            reviewAnchorCount: element.dataset[`${prefix}TrustChainReviewAnchorCount`] || "",
            surface: element.dataset[`${prefix}TrustChainSurface`] || "",
            scope: element.dataset[`${prefix}TrustChainScope`] || "",
          });
          const contextMirror = target(context, "context");
          const annotationMirror = target(annotation, "annotation");
          const canvasTarget = (element) => ({
            state: element.dataset.canvasTrustChainState || "",
            traceId: element.dataset.canvasTrustChainTraceId || "",
            sourceAnchorId: element.dataset.canvasTrustChainSourceAnchorId || "",
            surface: element.dataset.canvasTrustChainSurface || "",
            scope: element.dataset.canvasTrustChainScope || "",
          });
          const selectedMirror = canvasTarget(selected);
          const sourceMirror = canvasTarget(source);
          const same = (mirror) => mirror.state === left.state
            && mirror.traceId === left.traceId
            && mirror.sourceAnchorId === left.sourceAnchorId
            && mirror.nodeCount === left.nodeCount
            && mirror.wireCount === left.wireCount
            && mirror.outputCount === left.outputCount
            && mirror.reviewAnchorCount === left.reviewAnchorCount
            && left.scope === "current-segment"
            && mirror.surface === "current-segment"
            && mirror.scope === left.scope;
          const canvasSame = (mirror, expectedSurface) => mirror.state === left.state
            && mirror.traceId === left.traceId
            && mirror.sourceAnchorId === left.sourceAnchorId
            && left.sourceAnchorId.length > 0
            && mirror.surface === expectedSurface
            && mirror.scope === left.scope
            && left.scope === "current-segment";
          const expectedMatches = !expectedTraceId || left.traceId === expectedTraceId;
          return {
            ok: expectedMatches
              && same(contextMirror)
              && same(annotationMirror)
              && canvasSame(selectedMirror, "selected-target")
              && canvasSame(sourceMirror, "canvas-source"),
            expectedTraceId,
            left,
            context: contextMirror,
            annotation: annotationMirror,
            selected: selectedMirror,
            source: sourceMirror,
          };
        }""",
        expected_trace_id,
    )
    assert mirror_state["ok"] is True, mirror_state


def _expect_trace_identity_coherence_across_surfaces(page: Any) -> None:
    identity_state = page.evaluate(
        """() => {
          const consistency = document.querySelector("#logic-current-segment-consistency");
          const card = document.querySelector("#logic-current-segment-evidence");
          const chain = document.querySelector("#logic-current-segment-trust-chain");
          const globalReview = document.querySelector("#logic-current-segment-global-review");
          const identityLoop = document.querySelector("#logic-current-segment-identity-loop");
          const jumps = document.querySelector("#logic-current-segment-anchor-jumps");
          const selected = document.querySelector("#logic-selected-target-label");
          const source = document.querySelector("#logic-canvas-source");
          const context = document.querySelector("#logic-context-requirement-trace");
          const annotation = document.querySelector("#logic-annotation-requirement-trace");
          if (!consistency || !card || !chain || !globalReview || !identityLoop || !jumps || !selected || !source || !context || !annotation) {
            return { ok: false, reason: "missing-surface" };
          }
          const cardBox = card.getBoundingClientRect();
          const identityBox = identityLoop.getBoundingClientRect();
          const jumpsBox = jumps.getBoundingClientRect();
          const identityText = identityLoop.textContent || "";
          const identityChildren = Array.from(identityLoop.querySelectorAll("span, strong, small"));
          const identityChildrenClip = identityChildren.length === 6 && identityChildren.every((child) => {
            const childBox = child.getBoundingClientRect();
            const style = window.getComputedStyle(child);
            return childBox.width > 0
              && childBox.height > 0
              && childBox.left >= identityBox.left - 1
              && childBox.right <= identityBox.right + 1
              && style.whiteSpace === "nowrap"
              && style.overflowX === "hidden"
              && style.textOverflow === "ellipsis";
          });
          const identityInsideCard = identityBox.left >= cardBox.left - 1
            && identityBox.right <= cardBox.right + 1
            && identityBox.top >= cardBox.top - 1
            && identityBox.bottom <= cardBox.bottom + 1;
          const identityDoesNotCoverJumps = !(identityBox.left < jumpsBox.right
            && identityBox.right > jumpsBox.left
            && identityBox.top < jumpsBox.bottom
            && identityBox.bottom > jumpsBox.top);
          const identityCompact = identityBox.height > 0 && identityBox.height <= 28;
          const sourceAnchorId = chain.dataset.sourceAnchorId || "";
          const expected = {
            state: consistency.dataset.traceConsistencyState || "",
            currentId: consistency.dataset.traceConsistencyCurrentSegmentId || consistency.dataset.traceConsistencyCurrentId || "",
            selectedId: consistency.dataset.traceConsistencySelectedCanvasTraceId || consistency.dataset.traceConsistencySelectedId || "",
            selectedSource: consistency.dataset.traceConsistencySelectedSource || "",
          };
          const check = (key, actual, expectedValue) => ({
            key,
            actual,
            expected: expectedValue,
            ok: actual === expectedValue,
          });
          const stateChecks = [
            check("left-state", consistency.dataset.traceConsistencyState || "", expected.state),
            check("left-identity-loop-state", identityLoop.dataset.identityLoopState || "", expected.state),
            check("canvas-selected-state", selected.dataset.canvasTraceConsistencyState || "", expected.state),
            check("canvas-source-state", source.dataset.canvasTraceConsistencyState || "", expected.state),
            check("right-context-state", context.dataset.contextTraceConsistencyState || "", expected.state),
            check("right-annotation-state", annotation.dataset.annotationTraceConsistencyState || "", expected.state),
          ];
          const currentChecks = [
            check("left-current-id", consistency.dataset.traceConsistencyCurrentId || "", expected.currentId),
            check("left-current-segment-id", consistency.dataset.traceConsistencyCurrentSegmentId || "", expected.currentId),
            check("left-card-current-segment-id", card.dataset.currentSegmentId || "", expected.currentId),
            check("left-chain-trace-id", chain.dataset.currentSegmentTraceId || "", expected.currentId),
            check("left-global-review-current-segment-id", globalReview.dataset.currentSegmentId || "", expected.currentId),
            check("left-identity-loop-current-segment-id", identityLoop.dataset.currentSegmentId || "", expected.currentId),
            check("canvas-selected-current-id", selected.dataset.canvasTraceConsistencyCurrentId || "", expected.currentId),
            check("canvas-source-current-id", source.dataset.canvasTraceConsistencyCurrentId || "", expected.currentId),
            check("right-context-current-segment-id", context.dataset.contextTraceConsistencyCurrentSegmentId || "", expected.currentId),
            check("right-context-requirement-current-segment-id", context.dataset.contextRequirementTraceCurrentSegmentId || "", expected.currentId),
            check("right-annotation-current-segment-id", annotation.dataset.annotationTraceConsistencyCurrentSegmentId || "", expected.currentId),
            check("right-annotation-requirement-current-segment-id", annotation.dataset.annotationRequirementTraceCurrentSegmentId || "", expected.currentId),
          ];
          const selectedChecks = [
            check("left-selected-id", consistency.dataset.traceConsistencySelectedId || "", expected.selectedId),
            check("left-selected-canvas-trace-id", consistency.dataset.traceConsistencySelectedCanvasTraceId || "", expected.selectedId),
            check("left-identity-loop-selected-canvas-trace-id", identityLoop.dataset.selectedCanvasTraceId || "", expected.selectedId),
            check("canvas-selected-selected-id", selected.dataset.canvasTraceConsistencySelectedId || "", expected.selectedId),
            check("canvas-source-selected-id", source.dataset.canvasTraceConsistencySelectedId || "", expected.selectedId),
            check("right-context-selected-canvas-trace-id", context.dataset.contextTraceConsistencySelectedCanvasTraceId || "", expected.selectedId),
            check("right-context-requirement-selected-canvas-trace-id", context.dataset.contextRequirementTraceSelectedCanvasTraceId || "", expected.selectedId),
            check("right-annotation-selected-canvas-trace-id", annotation.dataset.annotationTraceConsistencySelectedCanvasTraceId || "", expected.selectedId),
            check("right-annotation-requirement-selected-canvas-trace-id", annotation.dataset.annotationRequirementTraceSelectedCanvasTraceId || "", expected.selectedId),
          ];
          const sourceChecks = [
            check("left-selected-source", consistency.dataset.traceConsistencySelectedSource || "", expected.selectedSource),
            check("left-card-selection-source", card.dataset.currentSegmentSelectionSource || "", expected.selectedSource),
            check("left-identity-loop-selected-source", identityLoop.dataset.selectedSource || "", expected.selectedSource),
            check("canvas-selected-selected-source", selected.dataset.canvasTraceConsistencySelectedSource || "", expected.selectedSource),
            check("canvas-source-selected-source", source.dataset.canvasTraceConsistencySelectedSource || "", expected.selectedSource),
            check("right-context-requirement-selected-source", context.dataset.contextRequirementTraceSelectedSource || "", expected.selectedSource),
            check("right-annotation-requirement-selected-source", annotation.dataset.annotationRequirementTraceSelectedSource || "", expected.selectedSource),
          ];
          const checks = [
            ...stateChecks,
            ...currentChecks,
            ...selectedChecks,
            ...sourceChecks,
            check("left-identity-loop-source-anchor-id", identityLoop.dataset.sourceAnchorId || "", sourceAnchorId),
            check("left-identity-loop-scope", identityLoop.dataset.identityLoopScope || "", "current-segment"),
          ];
          return {
            ok: expected.state.length > 0
              && expected.currentId.length > 0
              && expected.selectedId.length > 0
              && expected.selectedSource.length > 0
              && sourceAnchorId.length > 0
              && identityBox.width > 0
              && identityBox.height > 0
              && identityText.includes("身份闭环")
              && identityText.includes("当前段")
              && identityText.includes("选中")
              && identityText.includes("来源")
              && identityText.includes("锚点")
              && identityChildrenClip
              && identityInsideCard
              && identityDoesNotCoverJumps
              && identityCompact
              && checks.every((item) => item.ok),
            expected,
            sourceAnchorId,
            identityText,
            identityBox: {
              width: identityBox.width,
              height: identityBox.height,
            },
            identityLayout: {
              childCount: identityChildren.length,
              childrenClip: identityChildrenClip,
              insideCard: identityInsideCard,
              doesNotCoverJumps: identityDoesNotCoverJumps,
              compact: identityCompact,
              card: {
                width: cardBox.width,
                height: cardBox.height,
              },
              jumps: {
                top: jumpsBox.top,
                bottom: jumpsBox.bottom,
              },
            },
            checks,
          };
        }"""
    )
    assert identity_state["ok"] is True, identity_state


def _expect_current_segment_identity_loop_state(
    page: Any,
    *,
    state: str,
    current_id: str,
    selected_id: str,
    selected_source: str,
    source_anchor_id: str | None = None,
) -> None:
    expected_source_anchor_id = source_anchor_id
    if expected_source_anchor_id is None:
        expected_source_anchor_id = page.locator("#logic-current-segment-trust-chain").get_attribute("data-source-anchor-id") or ""
    if state in {"segment-only", "unbound"}:
        assert selected_id == "none"
        assert selected_source == "none"
    if state == "diverged":
        assert selected_id != "none"
        assert selected_source in {"canvas-node", "canvas-wire", "trace-list"}
    if state == "consistent":
        assert selected_id == current_id
    loop = page.locator("#logic-current-segment-identity-loop")
    expect(loop).to_be_visible()
    expect(loop).to_have_attribute("data-identity-loop-state", state)
    expect(loop).to_have_attribute("data-current-segment-id", current_id)
    expect(loop).to_have_attribute("data-selected-canvas-trace-id", selected_id)
    expect(loop).to_have_attribute("data-selected-source", selected_source)
    expect(loop).to_have_attribute("data-source-anchor-id", expected_source_anchor_id)
    expect(loop).to_have_attribute("data-identity-loop-scope", "current-segment")
    expect(loop).to_have_attribute("aria-label", re.compile(current_id))
    expect(loop).to_have_attribute("aria-label", re.compile(selected_id))
    expect(loop).to_have_attribute("aria-label", re.compile(expected_source_anchor_id))
    expect(loop).to_have_attribute("title", re.compile(current_id))
    expect(loop).to_have_attribute("title", re.compile(selected_id))
    expect(loop).to_have_attribute("title", re.compile(expected_source_anchor_id))
    expect(loop).to_contain_text("身份闭环")
    expect(loop).to_contain_text(current_id)
    expect(loop).to_contain_text(selected_id)
    expect(loop).to_contain_text(expected_source_anchor_id)


def _expect_inspector_trace_state_badge(page: Any, expected_label: str) -> None:
    badge_state = page.evaluate(
        """(label) => {
          const context = document.querySelector("#logic-context-requirement-trace");
          const annotation = document.querySelector("#logic-annotation-requirement-trace");
          if (!context || !annotation) return { ok: false, reason: "missing-surface" };
          const contextBadge = window.getComputedStyle(context, "::before").content || "";
          const annotationBadge = window.getComputedStyle(annotation, "::before").content || "";
          return {
            ok: contextBadge.includes(label) && annotationBadge.includes(label),
            label,
            contextBadge,
            annotationBadge,
            contextState: context.dataset.contextTraceConsistencyState || "",
            annotationState: annotation.dataset.annotationTraceConsistencyState || "",
          };
        }""",
        expected_label,
    )
    assert badge_state["ok"] is True, badge_state


def _expect_canvas_selected_trace_state_badge(
    page: Any,
    expected_label: str,
    *,
    state: str,
    current_id: str,
    selected_id: str,
    selected_source: str,
) -> None:
    badge_state = page.evaluate(
        """({label, state, currentId, selectedId, selectedSource}) => {
          const selected = document.querySelector("#logic-selected-target-label");
          const popover = document.querySelector("#logic-annotation-popover");
          const left = document.querySelector("#logic-current-segment-consistency");
          const context = document.querySelector("#logic-context-requirement-trace");
          const annotation = document.querySelector("#logic-annotation-requirement-trace");
          if (!selected || !popover || !left || !context || !annotation) {
            return { ok: false, reason: "missing-surface" };
          }
          const bridgeToken = "当前段到全局矩阵";
          const buildCountAudit = (visibleCounts, dataCounts, countsMatch, countsSource) => ({
            visibleCounts,
            dataCounts,
            countsMatch,
            countsSource,
          });
          const buildBridgeAudit = ({ visibleHasBridge, visibleHasGlobalMarker = null, titleHasBridge, ariaHasBridge, scope, expectedScope }) => ({
            token: bridgeToken,
            visibleHasBridge,
            visibleHasGlobalMarker,
            titleHasBridge,
            ariaHasBridge,
            scope,
            expectedScope,
            scopeMatch: scope === expectedScope,
          });
          const badge = window.getComputedStyle(selected, "::before").content || "";
          const tail = window.getComputedStyle(selected, "::after").content || "";
          const box = selected.getBoundingClientRect();
          const popoverBox = popover.getBoundingClientRect();
          const labelText = selected.textContent || "";
          const title = selected.getAttribute("title") || "";
          const ariaLabel = selected.getAttribute("aria-label") || "";
          const titleHasCurrentSegment = title.includes("当前段");
          const titleHasLink = title.includes("链路");
          const ariaHasCurrentSegment = ariaLabel.includes("当前段");
          const ariaHasLink = ariaLabel.includes("链路");
          const titleHasGlobalReview = title.includes("全局复核");
          const ariaHasGlobalReview = ariaLabel.includes("全局复核");
          const titleHasGlobalBridge = title.includes(bridgeToken);
          const ariaHasGlobalBridge = ariaLabel.includes(bridgeToken);
          const selectedTrustScope = selected.dataset.canvasTrustChainScope || "";
          const expectedTrustScope = "current-segment";
          const scopeIsCurrentSegment = selectedTrustScope === expectedTrustScope;
          const chainAccessible = titleHasCurrentSegment
            && titleHasLink
            && ariaHasCurrentSegment
            && ariaHasLink
            && titleHasGlobalReview
            && ariaHasGlobalReview
            && titleHasGlobalBridge
            && ariaHasGlobalBridge
            && scopeIsCurrentSegment;
          const outputCount = Number.parseInt(selected.dataset.canvasTrustChainOutputCount || "0", 10);
          const reviewCount = Number.parseInt(selected.dataset.canvasTrustChainReviewAnchorCount || "0", 10);
          const tailCounts = tail.match(/段链(\\d+)\\/(\\d+)全局/) || [];
          const tailOutputCount = Number.parseInt(tailCounts[1] || "-1", 10);
          const tailReviewCount = Number.parseInt(tailCounts[2] || "-1", 10);
          const tailCountsMatch = tailOutputCount === outputCount && tailReviewCount === reviewCount;
          const selectedCountAudit = buildCountAudit(
            { output: tailOutputCount, reviewAnchor: tailReviewCount },
            { output: outputCount, reviewAnchor: reviewCount },
            tailCountsMatch,
            "canvas-selected-tail",
          );
          const selectedBridgeAudit = buildBridgeAudit({
            visibleHasBridge: null,
            visibleHasGlobalMarker: tail.includes("全局"),
            titleHasBridge: titleHasGlobalBridge,
            ariaHasBridge: ariaHasGlobalBridge,
            scope: selectedTrustScope,
            expectedScope: expectedTrustScope,
          });
          const ok = badge.includes(label)
            && tail.includes("段链")
            && tail.includes("全局")
            && tailCountsMatch
            && chainAccessible
            && box.width > 0
            && box.height > 0
            && popoverBox.width > 0
            && box.left >= popoverBox.left - 2
            && box.right <= popoverBox.right + 2
            && selected.dataset.canvasTraceConsistencyState === state
            && selected.dataset.canvasTraceConsistencyCurrentId === currentId
            && selected.dataset.canvasTraceConsistencySelectedId === selectedId
            && selected.dataset.canvasTraceConsistencySelectedSource === selectedSource
            && selected.dataset.canvasTraceConsistencyCueLabel
            && selected.dataset.canvasTraceConsistencySurface === "selected-target"
            && selected.dataset.canvasTrustChainState === "ready"
            && selected.dataset.canvasTrustChainTraceId === currentId
            && selected.dataset.canvasTrustChainSurface === "selected-target"
            && selected.dataset.canvasTrustChainScope === "current-segment"
            && outputCount > 0
            && reviewCount > 0
            && left.dataset.traceConsistencyState === state
            && left.dataset.traceConsistencyCurrentId === currentId
            && left.dataset.traceConsistencySelectedId === selectedId
            && context.dataset.contextTraceConsistencyState === state
            && annotation.dataset.annotationTraceConsistencyState === state
            && labelText.length > 0;
          return {
            ok,
            badge,
            tail,
            title,
            ariaLabel,
            tailOutputCount,
            tailReviewCount,
            tailCountsMatch,
            globalReviewCounts: selectedCountAudit,
            countAudit: selectedCountAudit,
            bridgeAudit: selectedBridgeAudit,
            accessibility: {
              titleHasCurrentSegment,
              titleHasLink,
              ariaHasCurrentSegment,
              ariaHasLink,
              titleHasGlobalReview,
              ariaHasGlobalReview,
              titleHasGlobalBridge,
              ariaHasGlobalBridge,
              scopeIsCurrentSegment,
              chainAccessible,
            },
            traceSnapshot: {
              state: selected.dataset.canvasTraceConsistencyState || "",
              currentId: selected.dataset.canvasTraceConsistencyCurrentId || "",
              selectedId: selected.dataset.canvasTraceConsistencySelectedId || "",
              selectedSource: selected.dataset.canvasTraceConsistencySelectedSource || "",
              cueLabel: selected.dataset.canvasTraceConsistencyCueLabel || "",
              surface: selected.dataset.canvasTraceConsistencySurface || "",
            },
            trustSnapshot: {
              state: selected.dataset.canvasTrustChainState || "",
              traceId: selected.dataset.canvasTrustChainTraceId || "",
              surface: selected.dataset.canvasTrustChainSurface || "",
              scope: selectedTrustScope,
              outputCount: selected.dataset.canvasTrustChainOutputCount || "",
              reviewAnchorCount: selected.dataset.canvasTrustChainReviewAnchorCount || "",
            },
            surfaceStates: {
              left: left.dataset.traceConsistencyState || "",
              context: context.dataset.contextTraceConsistencyState || "",
              annotation: annotation.dataset.annotationTraceConsistencyState || "",
            },
            layout: {
              badge,
              tail,
              selected: {
                width: box.width,
                height: box.height,
                left: box.left,
                right: box.right,
              },
              selectedWidth: box.width,
              selectedHeight: box.height,
              selectedLeft: box.left,
              selectedRight: box.right,
              popover: {
                width: popoverBox.width,
                left: popoverBox.left,
                right: popoverBox.right,
              },
              popoverWidth: popoverBox.width,
              popoverLeft: popoverBox.left,
              popoverRight: popoverBox.right,
            },
          };
        }""",
        {
            "label": expected_label,
            "state": state,
            "currentId": current_id,
            "selectedId": selected_id,
            "selectedSource": selected_source,
        },
    )
    assert badge_state["ok"] is True, badge_state


def _expect_canvas_source_trace_state_badge(
    page: Any,
    expected_label: str,
    *,
    state: str,
    current_id: str,
    selected_id: str,
    selected_source: str,
) -> None:
    badge_state = page.evaluate(
        """({label, state, currentId, selectedId, selectedSource}) => {
          const source = document.querySelector("#logic-canvas-source");
          const sourceState = document.querySelector("#logic-canvas-source-state");
          const traceLegend = document.querySelector("#logic-canvas-trace-legend");
          const selected = document.querySelector("#logic-selected-target-label");
          const left = document.querySelector("#logic-current-segment-consistency");
          const context = document.querySelector("#logic-context-requirement-trace");
          const annotation = document.querySelector("#logic-annotation-requirement-trace");
          if (!source || !sourceState || !traceLegend || !selected || !left || !context || !annotation) {
            return { ok: false, reason: "missing-surface" };
          }
          const bridgeToken = "当前段到全局矩阵";
          const buildCountAudit = (visibleCounts, dataCounts, countsMatch, countsSource) => ({
            visibleCounts,
            dataCounts,
            countsMatch,
            countsSource,
          });
          const buildBridgeAudit = ({ visibleHasBridge, visibleHasGlobalMarker = null, titleHasBridge, ariaHasBridge, scope, expectedScope }) => ({
            token: bridgeToken,
            visibleHasBridge,
            visibleHasGlobalMarker,
            titleHasBridge,
            ariaHasBridge,
            scope,
            expectedScope,
            scopeMatch: scope === expectedScope,
          });
          const badge = window.getComputedStyle(source, "::before").content || "";
          const box = source.getBoundingClientRect();
          const title = source.getAttribute("title") || "";
          const ariaLabel = source.getAttribute("aria-label") || "";
          const titleHasCurrentSegment = title.includes("当前段");
          const titleHasLink = title.includes("链路");
          const ariaHasCurrentSegment = ariaLabel.includes("当前段");
          const ariaHasLink = ariaLabel.includes("链路");
          const titleHasGlobalReview = title.includes("全局复核");
          const ariaHasGlobalReview = ariaLabel.includes("全局复核");
          const titleHasGlobalBridge = title.includes(bridgeToken);
          const ariaHasGlobalBridge = ariaLabel.includes(bridgeToken);
          const sourceTrustScope = source.dataset.canvasTrustChainScope || "";
          const expectedTrustScope = "current-segment";
          const scopeIsCurrentSegment = sourceTrustScope === expectedTrustScope;
          const chainAccessible = titleHasCurrentSegment
            && titleHasLink
            && ariaHasCurrentSegment
            && ariaHasLink
            && titleHasGlobalReview
            && ariaHasGlobalReview
            && titleHasGlobalBridge
            && ariaHasGlobalBridge
            && scopeIsCurrentSegment;
          const outputCount = Number.parseInt(source.dataset.canvasTrustChainOutputCount || "0", 10);
          const reviewCount = Number.parseInt(source.dataset.canvasTrustChainReviewAnchorCount || "0", 10);
          const childReadable = (element) => {
            const childBox = element.getBoundingClientRect();
            return childBox.width > 0
              && childBox.height > 0
              && element.scrollWidth <= element.clientWidth + 1
              && (element.textContent || "").trim().length > 0;
          };
          const ok = badge.includes(label)
            && box.width > 0
            && box.height > 0
            && box.width <= 180
            && childReadable(sourceState)
            && childReadable(traceLegend)
            && source.dataset.canvasTraceConsistencyState === state
            && source.dataset.canvasTraceConsistencyCurrentId === currentId
            && source.dataset.canvasTraceConsistencySelectedId === selectedId
            && source.dataset.canvasTraceConsistencySelectedSource === selectedSource
            && source.dataset.canvasTraceConsistencyCueLabel
            && source.dataset.canvasTraceConsistencySurface === "canvas-source"
            && chainAccessible
            && source.dataset.canvasTrustChainState === "ready"
            && source.dataset.canvasTrustChainTraceId === currentId
            && source.dataset.canvasTrustChainSurface === "canvas-source"
            && source.dataset.canvasTrustChainScope === "current-segment"
            && outputCount > 0
            && reviewCount > 0
            && selected.dataset.canvasTraceConsistencyState === state
            && selected.dataset.canvasTraceConsistencyCurrentId === currentId
            && selected.dataset.canvasTraceConsistencySelectedId === selectedId
            && selected.dataset.canvasTraceConsistencySelectedSource === selectedSource
            && left.dataset.traceConsistencyState === state
            && context.dataset.contextTraceConsistencyState === state
            && annotation.dataset.annotationTraceConsistencyState === state;
          const sourceCountAudit = buildCountAudit(
            { output: null, reviewAnchor: null },
            { output: outputCount, reviewAnchor: reviewCount },
            null,
            "canvas-source-data-only",
          );
          const sourceBridgeAudit = buildBridgeAudit({
            visibleHasBridge: null,
            visibleHasGlobalMarker: null,
            titleHasBridge: titleHasGlobalBridge,
            ariaHasBridge: ariaHasGlobalBridge,
            scope: sourceTrustScope,
            expectedScope: expectedTrustScope,
          });
          return {
            ok,
            badge,
            title,
            ariaLabel,
            countAudit: sourceCountAudit,
            bridgeAudit: sourceBridgeAudit,
            accessibility: {
              titleHasCurrentSegment,
              titleHasLink,
              ariaHasCurrentSegment,
              ariaHasLink,
              titleHasGlobalReview,
              ariaHasGlobalReview,
              titleHasGlobalBridge,
              ariaHasGlobalBridge,
              scopeIsCurrentSegment,
              chainAccessible,
            },
            traceSnapshot: {
              state: source.dataset.canvasTraceConsistencyState || "",
              currentId: source.dataset.canvasTraceConsistencyCurrentId || "",
              selectedId: source.dataset.canvasTraceConsistencySelectedId || "",
              selectedSource: source.dataset.canvasTraceConsistencySelectedSource || "",
              cueLabel: source.dataset.canvasTraceConsistencyCueLabel || "",
              surface: source.dataset.canvasTraceConsistencySurface || "",
            },
            trustSnapshot: {
              state: source.dataset.canvasTrustChainState || "",
              traceId: source.dataset.canvasTrustChainTraceId || "",
              surface: source.dataset.canvasTrustChainSurface || "",
              scope: sourceTrustScope,
              outputCount: source.dataset.canvasTrustChainOutputCount || "",
              reviewAnchorCount: source.dataset.canvasTrustChainReviewAnchorCount || "",
            },
            layout: {
              badge,
              source: {
                width: box.width,
                height: box.height,
                left: box.left,
                right: box.right,
              },
              width: box.width,
              height: box.height,
              sourceWidth: box.width,
              sourceHeight: box.height,
              sourceLeft: box.left,
              sourceRight: box.right,
            },
            surfaceStates: {
              selected: selected.dataset.canvasTraceConsistencyState || "",
              left: left.dataset.traceConsistencyState || "",
              context: context.dataset.contextTraceConsistencyState || "",
              annotation: annotation.dataset.annotationTraceConsistencyState || "",
            },
          };
        }""",
        {
            "label": expected_label,
            "state": state,
            "currentId": current_id,
            "selectedId": selected_id,
            "selectedSource": selected_source,
        },
    )
    assert badge_state["ok"] is True, badge_state


def _assert_inspector_trace_badge_layout(page: Any, expected_label: str) -> None:
    layout_state = page.evaluate(
        """(label) => {
          const bridgeToken = "当前段到全局矩阵";
          const buildCountAudit = (visibleCounts, dataCounts, countsMatch, countsSource) => ({
            visibleCounts,
            dataCounts,
            countsMatch,
            countsSource,
          });
          const buildBridgeAudit = ({ visibleHasBridge, visibleHasGlobalMarker = null, titleHasBridge, ariaHasBridge, scope, expectedScope }) => ({
            token: bridgeToken,
            visibleHasBridge,
            visibleHasGlobalMarker,
            titleHasBridge,
            ariaHasBridge,
            scope,
            expectedScope,
            scopeMatch: scope === expectedScope,
          });
          const surfaces = [
            { element: document.querySelector("#logic-context-requirement-trace"), prefix: "context" },
            { element: document.querySelector("#logic-annotation-requirement-trace"), prefix: "annotation" },
          ];
          const checks = surfaces.map(({ element, prefix }) => {
            if (!element) return { ok: false, reason: "missing", prefix };
            const box = element.getBoundingClientRect();
            const style = window.getComputedStyle(element);
            const badge = window.getComputedStyle(element, "::before");
            const tail = window.getComputedStyle(element, "::after");
            const badgeContent = badge.content || "";
            const tailContent = tail.content || "";
            const outputCount = Number.parseInt(element.dataset[`${prefix}TrustChainOutputCount`] || "0", 10);
            const reviewAnchorCount = Number.parseInt(element.dataset[`${prefix}TrustChainReviewAnchorCount`] || "0", 10);
            const tailCounts = tailContent.match(/段链\\s*(\\d+)输出\\/(\\d+)全局复核/) || [];
            const tailOutputCount = Number.parseInt(tailCounts[1] || "-1", 10);
            const tailReviewCount = Number.parseInt(tailCounts[2] || "-1", 10);
            const tailCountsMatch = tailOutputCount === outputCount && tailReviewCount === reviewAnchorCount;
            const lineHeight = Number.parseFloat(style.lineHeight || "0") || 16;
            const text = element.textContent || "";
            const title = element.getAttribute("title") || "";
            const ariaLabel = element.getAttribute("aria-label") || "";
            const titleHasCurrentSegment = title.includes("当前段");
            const titleHasLink = title.includes("链路");
            const ariaHasCurrentSegment = ariaLabel.includes("当前段");
            const ariaHasLink = ariaLabel.includes("链路");
            const titleHasGlobalReview = title.includes("全局复核");
            const ariaHasGlobalReview = ariaLabel.includes("全局复核");
            const titleHasGlobalBridge = title.includes(bridgeToken);
            const ariaHasGlobalBridge = ariaLabel.includes(bridgeToken);
            const scope = element.dataset[`${prefix}TrustChainScope`] || "";
            const expectedScope = "current-segment";
            const scopeIsCurrentSegment = scope === expectedScope;
            const chainAccessible = titleHasCurrentSegment
              && titleHasLink
              && ariaHasCurrentSegment
              && ariaHasLink
              && titleHasGlobalReview
              && ariaHasGlobalReview
              && titleHasGlobalBridge
              && ariaHasGlobalBridge
              && scopeIsCurrentSegment;
            const ok = box.width > 0
              && box.height > 0
              && style.visibility !== "hidden"
              && badgeContent.includes(label)
              && tailContent.includes("段链")
              && tailContent.includes("输出")
              && tailContent.includes("复核")
              && tailContent.includes("全局复核")
              && tailCountsMatch
              && chainAccessible
              && text.includes("段")
              && element.scrollWidth <= element.clientWidth + 2
              && box.height <= lineHeight * 2 + 8
              && element.dataset[`${prefix}TrustChainSurface`] === "current-segment"
              && scopeIsCurrentSegment;
            const rightCountAudit = buildCountAudit(
              { output: tailOutputCount, reviewAnchor: tailReviewCount },
              { output: outputCount, reviewAnchor: reviewAnchorCount },
              tailCountsMatch,
              `${prefix}-tail`,
            );
            const rightBridgeAudit = buildBridgeAudit({
              visibleHasBridge: null,
              visibleHasGlobalMarker: tailContent.includes("全局复核"),
              titleHasBridge: titleHasGlobalBridge,
              ariaHasBridge: ariaHasGlobalBridge,
              scope,
              expectedScope,
            });
            return {
              ok,
              prefix,
              badgeContent,
              tailContent,
              outputCount,
              reviewAnchorCount,
              tailOutputCount,
              tailReviewCount,
              tailCountsMatch,
              globalReviewCounts: rightCountAudit,
              countAudit: rightCountAudit,
              bridgeAudit: rightBridgeAudit,
              title,
              ariaLabel,
              text,
              titleHasCurrentSegment,
              titleHasLink,
              ariaHasCurrentSegment,
              ariaHasLink,
              titleHasGlobalReview,
              ariaHasGlobalReview,
              titleHasGlobalBridge,
              ariaHasGlobalBridge,
              chainAccessible,
              height: box.height,
              lineHeight,
              scrollWidth: element.scrollWidth,
              clientWidth: element.clientWidth,
              surface: element.dataset[`${prefix}TrustChainSurface`] || "",
              scope,
              expectedScope,
              scopeIsCurrentSegment,
            };
          });
          return { ok: checks.every((check) => check.ok), checks };
        }""",
        expected_label,
    )
    assert layout_state["ok"] is True, layout_state


def _expect_cross_surface_trace_audit(
    *,
    segment_consistency: Any,
    trust_review_state: Any,
    trust_spine: Any,
    context_trace: Any,
    annotation_trace: Any,
    state: str,
    consistency_id: str | None = None,
    review_id: str | None = None,
    trace_id: str | None = None,
    current_id: str | None = None,
    selected_id: str | None = None,
    selected_source: str | None = None,
    cue: str | None = None,
    cue_label: str | None = None,
    alignable: bool | None = None,
    align_target_id: str | None = None,
    align_source: str | None = None,
) -> None:
    _expect_trace_consistency(
        segment_consistency,
        state=state,
        consistency_id=consistency_id,
        current_id=current_id,
        selected_id=selected_id,
        selected_source=selected_source,
        cue=cue,
        cue_label=cue_label,
        alignable=alignable,
        align_target_id=align_target_id,
        align_source=align_source,
    )
    _expect_trust_review_consistency(
        trust_review_state,
        state=state,
        review_id=review_id,
        current_id=current_id,
        selected_id=selected_id,
    )
    _expect_trust_spine_consistency(
        trust_spine,
        state=state,
        current_id=current_id,
        selected_id=selected_id,
        selected_source=selected_source,
    )
    _expect_requirement_trace_audit(
        context_trace,
        prefix="context",
        state=state,
        trace_id=trace_id,
        current_id=current_id,
        selected_id=selected_id,
        selected_source=selected_source,
    )
    _expect_requirement_trace_audit(
        annotation_trace,
        prefix="annotation",
        state=state,
        trace_id=trace_id,
        current_id=current_id,
        selected_id=selected_id,
        selected_source=selected_source,
    )


def _expect_consistency_align_button(
    locator: Any,
    *,
    visible: bool,
    enabled: bool,
    action: str | None = None,
    align: str | None = None,
    target_id: str | None = None,
    source: str | None = None,
) -> None:
    if visible:
        expect(locator).to_be_visible()
    else:
        expect(locator).to_be_hidden()
    if enabled:
        expect(locator).to_be_enabled()
    else:
        expect(locator).to_be_disabled()
    if action is not None:
        expect(locator).to_have_attribute("data-trace-consistency-action", action)
    if align is not None:
        expect(locator).to_have_attribute("data-trace-consistency-align", align)
    if target_id is not None:
        expect(locator).to_have_attribute("data-trace-consistency-align-target-id", target_id)
    if source is not None:
        expect(locator).to_have_attribute("data-trace-consistency-align-source", source)


REQUIREMENTS_READY = {
    "kind": "ai-fantui-requirements-intake-analysis",
    "status": "ready_for_logic_builder",
    "ready_for_logic_builder": True,
    "summary_zh": "DeepSeek V4 Pro 已将反推逻辑需求整理为可绘制的概念链路。",
    "source_requirements_sha256": "deepseek-demo-sha256",
    "source_document": {
        "name": "deepseek-v4-pro-demo-requirements.md",
    },
    "open_questions": [],
    "concept_logic_nodes": [
        {
            "id": "input_ra",
            "label": "RA 高度",
            "node_kind": "input",
            "description_zh": "读取无线电高度并供门限判断使用。",
            "parameters": [{"id": "ra_threshold", "label": "RA 门限", "default": 6, "unit": "ft"}],
        },
        {
            "id": "gate_release",
            "label": "释放门",
            "node_kind": "logic",
            "description_zh": "汇总 TRA、SW1、SW2 与 EEC 条件。",
            "parameters": [],
        },
        {
            "id": "output_unlock",
            "label": "油门锁释放",
            "node_kind": "output",
            "description_zh": "输出概念级释放命令。",
            "parameters": [],
        },
    ],
    "concept_edges": [
        {"source": "input_ra", "target": "gate_release", "label": "RA < 6ft", "endpoint_status": "resolved"},
        {"source": "gate_release", "target": "output_unlock", "label": "all gates true", "endpoint_status": "resolved"},
    ],
    "controller_truth_modified": False,
    "certification_claim": "none",
    "llm": {"provider": "deepseek", "model": "DeepSeek V4 Pro"},
}

LOGIC_DRAWING = {
    "kind": "ai-fantui-logic-link-drawing",
    "status": "draft_ready",
    "summary_zh": "DeepSeek V4 Pro 已生成初版逻辑链路图，节点层级和连线可读。",
    "source_requirements_sha256": "deepseek-demo-sha256",
    "canvas": {"width": 1180, "height": 620},
    "nodes": [
        {
            "id": "input_ra",
            "label": "RA 高度",
            "node_kind": "input",
            "description_zh": "高度输入节点。",
            "x": 70,
            "y": 170,
            "width": 190,
            "height": 110,
        },
        {
            "id": "gate_release",
            "label": "释放门",
            "node_kind": "logic",
            "description_zh": "TRA、SW1、SW2、EEC 条件汇合。",
            "x": 450,
            "y": 155,
            "width": 220,
            "height": 126,
        },
        {
            "id": "output_unlock",
            "label": "油门锁释放",
            "node_kind": "output",
            "description_zh": "概念输出命令。",
            "x": 830,
            "y": 170,
            "width": 210,
            "height": 110,
        },
    ],
    "edges": [
        {
            "id": "edge_ra_gate",
            "source": "input_ra",
            "target": "gate_release",
            "route": [{"x": 260, "y": 225}, {"x": 450, "y": 225}],
        },
        {
            "id": "edge_gate_output",
            "source": "gate_release",
            "target": "output_unlock",
            "route": [{"x": 670, "y": 225}, {"x": 830, "y": 225}],
        },
    ],
    "parameter_panels": [
        {
            "id": "panel_ra_threshold",
            "node_id": "input_ra",
            "label": "RA 门限",
            "min": 0,
            "max": 20,
            "default": 6,
            "unit": "ft",
            "x": 80,
            "y": 330,
            "width": 180,
            "height": 80,
        },
    ],
    "drawing_notes": ["初版图纸用于演示级需求到逻辑链路走读，不修改控制逻辑真值。"],
    "controller_truth_modified": False,
    "certification_claim": "none",
    "llm": {"provider": "deepseek", "model": "DeepSeek V4 Pro"},
}

FAULT_PREPARATION = {
    "kind": "ai-fantui-fault-injection-preparation",
    "status": "fault_preparation_ready",
    "summary_zh": "已基于当前逻辑图准备故障候选和注入边界问题。",
    "fault_scenarios": [
        {
            "id": "fault_ra_stuck_low",
            "label": "RA 低值卡滞",
            "node_id": "input_ra",
            "fault_type": "stuck_low",
            "severity": "high",
            "rationale_zh": "RA 输入会直接影响释放门判断。",
            "expected_effect_zh": "可能提前满足释放条件。",
            "observable_signals": ["ra_ft", "release_gate"],
        }
    ],
    "injection_points": [
        {
            "id": "inject_ra",
            "node_id": "input_ra",
            "signal_name": "ra_ft",
            "injection_mode": "override",
            "safe_boundary_zh": "仅空跑，不触发真实执行。",
        }
    ],
    "boundary_questions": [
        {
            "id": "boundary_dry_run",
            "prompt_zh": "确认本次只生成空跑沙盒建议？",
            "rationale_zh": "防止演示链路被误解为真实控制执行。",
        },
        {
            "id": "boundary_range",
            "prompt_zh": "确认 RA 注入范围限制在 0 到 20ft？",
            "rationale_zh": "保证沙盒观察点有明确范围。",
        },
    ],
    "workflow_notes": ["完成边界确认后进入沙盒注入配置。"],
    "coverage_completion": {
        "strategy": "deterministic_dry_run_candidate",
        "completed_node_ids": ["thr_lock_rel"],
        "semantic_gate": "critical_node_coverage",
    },
    "controller_truth_modified": False,
    "certification_claim": "none",
    "llm": {"provider": "deepseek", "model": "DeepSeek V4 Pro"},
}

SANDBOX_PLAN = {
    "kind": "ai-fantui-fault-injection-sandbox-plan",
    "status": "sandbox_plan_ready",
    "summary_zh": "已生成空跑沙盒配置建议和人工审查清单。",
    "sandbox_injection_plan": [
        {
            "id": "plan_ra_override",
            "fault_scenario_id": "fault_ra_stuck_low",
            "node_id": "input_ra",
            "injection_mode": "override",
            "safe_range_zh": "RA 输入限制在 0 到 20ft。",
            "expected_effect_zh": "观察释放门是否只在完整条件满足后放行。",
        }
    ],
    "observation_points": [
        {
            "id": "observe_release_gate",
            "node_id": "gate_release",
            "signal_name": "release_gate",
            "check_zh": "确认 RA 异常不会绕过 TRA、SW1、SW2、EEC 条件。",
        }
    ],
    "review_checklist": [
        {
            "id": "review_dry_run",
            "category": "dry_run",
            "condition_zh": "确认沙盒配置只读且不运行 tick。",
            "pass_criteria_zh": "run_tick:false、simulate:false、dry_run_only:true。",
        }
    ],
    "execution_contract": {"run_tick": False, "simulate": False, "dry_run_only": True},
    "plan_coverage_completion": {
        "strategy": "deterministic_dry_run_plan",
        "completed_fault_scenario_ids": ["auto_fault_thr_lock_rel"],
        "semantic_gate": "scenario_plan_coverage",
    },
    "controller_truth_modified": False,
    "certification_claim": "none",
    "llm": {"provider": "deepseek", "model": "DeepSeek V4 Pro"},
}


def _dense_sandbox_plan() -> dict[str, Any]:
    payload = json.loads(json.dumps(SANDBOX_PLAN))
    payload["sandbox_injection_plan"] = [
        {
            "id": f"plan_{index}",
            "fault_scenario_id": f"fault_{index}",
            "node_id": f"node_{index}",
            "injection_mode": "override",
            "safe_range_zh": "仅空跑，范围由准备页边界限制。",
            "expected_effect_zh": "观察对应逻辑节点是否保持可解释状态。",
        }
        for index in range(1, 10)
    ]
    payload["observation_points"] = [
        {
            "id": f"observe_{index}",
            "node_id": f"node_{index}",
            "signal_name": f"signal_{index}",
            "check_zh": "记录空跑输出，不触发仿真 tick。",
        }
        for index in range(1, 10)
    ]
    payload["review_checklist"] = [
        {
            "id": f"review_{index}",
            "category": "risk" if index % 2 else "coverage",
            "condition_zh": f"确认审查细项 {index}。",
            "pass_criteria_zh": "只作为折叠细项展示，不要求逐项勾选。",
        }
        for index in range(1, 9)
    ]
    return payload


def _l1_l4_circuit_requirements() -> dict[str, Any]:
    return {
        "kind": "ai-fantui-requirements-intake-analysis",
        "status": "ready_for_logic_builder",
        "ready_for_logic_builder": True,
        "summary_zh": "本地预解析已收敛出 L1-L4 反推链路。",
        "concept_logic_nodes": [
            {"id": "logic1", "label": "L1", "node_kind": "logic"},
            {"id": "logic2", "label": "L2", "node_kind": "logic"},
            {"id": "logic3", "label": "L3", "node_kind": "logic"},
            {"id": "logic4", "label": "L4", "node_kind": "logic"},
        ],
        "concept_edges": [],
        "deterministic_preparse": {"available": True, "applied": True},
        "truth_effect": "none",
        "candidate_state": "concept_only",
        "certification_claim": "none",
        "controller_truth_modified": False,
    }


def _circuit_view_drawing() -> dict[str, Any]:
    return {
        "kind": "ai-fantui-logic-link-drawing",
        "status": "draft_ready",
        "summary_zh": "确定性 L1-L4 电路图已生成。",
        "source_requirements_sha256": "l1-l4-circuit-sha",
        "canvas": {"width": 900, "height": 400},
        "nodes": [],
        "edges": [],
        "parameter_panels": [],
        "drawing_notes": ["确定性电路视图复刻 demo.html 链路。"],
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "circuit_view": _build_l1_l4_circuit_view(_l1_l4_circuit_requirements()),
    }


@pytest.fixture(scope="module")
def browser() -> Iterator[Any]:
    with sync_playwright() as pw:
        try:
            instance = pw.chromium.launch()
        except Exception as exc:
            pytest.skip(f"chromium browser not installed: {exc}")
        try:
            yield instance
        finally:
            instance.close()


def _fulfill_json(route: Any, payload: dict[str, Any]) -> None:
    route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps(payload, ensure_ascii=False),
    )


def _install_model_routes(page: Any) -> None:
    page.route("**/api/requirements-intake/provider-status?provider=deepseek", lambda route: _fulfill_json(route, {
        "provider": "deepseek",
        "model": "deepseek-v4-pro",
        "api_base": "https://api.deepseek.com",
        "key_available": True,
        "key_source": "env:DEEPSEEK_API_KEY",
        "live_ready": True,
    }))
    page.route("**/api/requirements-intake/analyze", lambda route: _fulfill_json(route, REQUIREMENTS_READY))
    page.route("**/api/requirements-intake/draw-logic", lambda route: _fulfill_json(route, _circuit_view_drawing()))
    page.route(
        "**/api/requirements-intake/prepare-fault-injection",
        lambda route: _fulfill_json(route, FAULT_PREPARATION),
    )
    page.route(
        "**/api/requirements-intake/prepare-fault-injection/sandbox",
        lambda route: _fulfill_json(route, SANDBOX_PLAN),
    )


def _replay_payload() -> dict[str, Any]:
    fault_payload = {
        **FAULT_PREPARATION,
        "boundary_answers": [
            {
                "id": "boundary_dry_run",
                "prompt_zh": "确认本次只生成空跑沙盒建议？",
                "answer_zh": "确认只用于空跑回放演示。",
            },
            {
                "id": "boundary_range",
                "prompt_zh": "确认 RA 注入范围限制在 0 到 20ft？",
                "answer_zh": "确认 RA 注入范围限制在 0 到 20ft。",
            },
        ],
    }
    return {
        "kind": "ai-fantui-deepseek-live-demo-replay",
        "source": "artifacts/deepseek-live-full-chain",
        "requirements_payload": REQUIREMENTS_READY,
        "drawing_payload": _circuit_view_drawing(),
        "fault_preparation_payload": FAULT_PREPARATION,
        "sandbox_plan_payload": SANDBOX_PLAN,
        "boundary_answers": fault_payload["boundary_answers"],
        "run_summary": {"ok": True, "model": "deepseek-v4-pro"},
        "replay_summary": {
            "ok": True,
            "model": "deepseek-v4-pro",
            "generated_at": "2026-05-13T10:30:00Z",
            "stage_counts": [
                {"id": "requirements", "label_zh": "需求理解", "primary": 3, "secondary": 2, "summary_zh": "3 concepts / 2 edges"},
                {"id": "drawing", "label_zh": "逻辑图", "primary": 20, "secondary": 23, "summary_zh": "20 circuit nodes / 23 wires"},
                {"id": "fault", "label_zh": "故障准备", "primary": 1, "secondary": 1, "summary_zh": "1 scenarios / 1 points / 2 questions"},
                {"id": "sandbox", "label_zh": "沙盒计划", "primary": 1, "secondary": 1, "summary_zh": "1 plans / 1 observations / 1 reviews"},
            ],
        },
        "local_storage_keys": {
            "requirements": "ai-fantui-requirements-intake-ready-v1",
            "drawing": "ai-fantui-logic-builder-drawing-v1",
            "change_history": "ai-fantui-logic-builder-change-history-v1",
            "fault": "ai-fantui-fault-injection-preparation-v1",
            "sandbox": "ai-fantui-fault-injection-sandbox-plan-v1",
        },
    }


def _assert_deepseek_page_contract(page: Any, active_key: str) -> dict[str, Any]:
    page.evaluate("window.scrollTo(0, 0)")
    expect(page.locator("body")).to_have_attribute("data-primary-flow", PRIMARY_FLOW)
    expect(page.locator("body")).to_have_attribute("data-canvas-status", CANVAS_STATUS)
    expect(page.locator("body")).to_have_attribute("data-nav-current", active_key)

    forbidden_links = page.eval_on_selector_all(
        "a[href]",
        """(links) => links
          .map((link) => link.getAttribute("href"))
          .filter((href) => href === "/workbench" || href === "/workbench/start")""",
    )
    assert forbidden_links == []

    expect(page.locator("#deepseek-nav-mainline")).to_be_visible()
    expect(page.locator("#deepseek-nav-mainline .unified-nav-link")).to_have_count(4)
    expect(page.locator(f'#deepseek-nav-mainline [data-nav-key="{active_key}"]')).to_be_visible()
    expect(page.locator("#deepseek-nav-advanced-modules")).to_be_visible()
    assert page.locator("#deepseek-nav-advanced-modules").evaluate("element => element.open") is False
    expect(page.locator('#deepseek-nav-advanced-modules a[href="/demo.html"]')).to_be_hidden()
    expect(page.locator('#deepseek-nav-advanced-modules a[href="/fantui_circuit.html"]')).to_be_hidden()

    nav_box = page.locator("header.unified-nav").bounding_box()
    topbar_box = page.locator("main > section").first.bounding_box()
    workflow_box = page.locator('[aria-label="流程总览"]').bounding_box()
    assert nav_box is not None
    assert topbar_box is not None
    if nav_box["width"] < 200:
        assert nav_box["height"] >= 700
        assert topbar_box["x"] >= nav_box["x"] + nav_box["width"] - 2
        assert topbar_box["y"] >= 0
    else:
        assert nav_box["width"] >= 900
        assert topbar_box["y"] >= nav_box["y"] + nav_box["height"] - 2
    if active_key == "logic-builder":
        assert workflow_box is not None
        assert workflow_box["y"] >= topbar_box["y"] - 2
        assert workflow_box["y"] + workflow_box["height"] <= topbar_box["y"] + topbar_box["height"] + 2
        assert workflow_box["height"] >= 48
    else:
        expect(page.locator('[aria-label="流程总览"]')).to_have_count(1)
        if workflow_box is not None:
            assert workflow_box["y"] >= topbar_box["y"] + topbar_box["height"] - 2
            assert workflow_box["height"] >= 1

    background = page.evaluate(
        """
        () => {
          const raw = getComputedStyle(document.body).backgroundColor;
          const parts = raw.match(/\\d+(?:\\.\\d+)?/g)?.slice(0, 3).map(Number) || [255, 255, 255];
          return {raw, average: (parts[0] + parts[1] + parts[2]) / 3};
        }
        """
    )
    assert background["average"] < 80 or background["average"] > 220

    return {
        "path": page.url,
        "active_key": active_key,
        "nav": nav_box,
        "topbar": topbar_box,
        "workflow": workflow_box,
        "background": background["raw"],
    }


def _screenshot(page: Any, name: str) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(ARTIFACT_DIR / f"{name}.png"), full_page=True)


def _assert_logic_circuit_blueprint_geometry(page: Any) -> None:
    geometry = page.evaluate(
        """() => {
          const failures = [];
          const nodeRects = new Map(Array.from(document.querySelectorAll(".logic-circuit-node")).map((node) => {
            const box = node.querySelector(".logic-circuit-node-box, .logic-circuit-gate-box");
            return [node.dataset.demoNodeId || node.dataset.nodeId || "", {
              x: Number(box?.getAttribute("x") || 0),
              y: Number(box?.getAttribute("y") || 0),
              width: Number(box?.getAttribute("width") || 0),
              height: Number(box?.getAttribute("height") || 0),
            }];
          }));
          const junctions = Array.from(document.querySelectorAll(".logic-circuit-junction")).map((junction) => ({
            x: Number(junction.getAttribute("cx") || 0),
            y: Number(junction.getAttribute("cy") || 0),
            source: junction.dataset.source || "",
          }));
          const parsePoints = (raw) => String(raw || "").trim().split(/\\s+/).map((pair) => {
            const [x, y] = pair.split(",").map(Number);
            return {x, y};
          }).filter((point) => Number.isFinite(point.x) && Number.isFinite(point.y));
          const pointOnRectEdge = (point, rect, tolerance = 3) => {
            const minX = rect.x;
            const maxX = rect.x + rect.width;
            const minY = rect.y;
            const maxY = rect.y + rect.height;
            const withinX = point.x >= minX - tolerance && point.x <= maxX + tolerance;
            const withinY = point.y >= minY - tolerance && point.y <= maxY + tolerance;
            const onVertical = Math.abs(point.x - minX) <= tolerance || Math.abs(point.x - maxX) <= tolerance;
            const onHorizontal = Math.abs(point.y - minY) <= tolerance || Math.abs(point.y - maxY) <= tolerance;
            return withinX && withinY && (onVertical || onHorizontal);
          };
          const pointOnJunction = (point, source) => junctions.some((junction) => (
            (!source || junction.source === source)
            && Math.hypot(point.x - junction.x, point.y - junction.y) <= 4
          ));
          const segmentCutsRect = (a, b, rect) => {
            const left = rect.x + 4;
            const right = rect.x + rect.width - 4;
            const top = rect.y + 4;
            const bottom = rect.y + rect.height - 4;
            if (Math.abs(a.y - b.y) < 0.01) {
              const y = a.y;
              const minX = Math.min(a.x, b.x);
              const maxX = Math.max(a.x, b.x);
              return y > top && y < bottom && maxX > left && minX < right;
            }
            if (Math.abs(a.x - b.x) < 0.01) {
              const x = a.x;
              const minY = Math.min(a.y, b.y);
              const maxY = Math.max(a.y, b.y);
              return x > left && x < right && maxY > top && minY < bottom;
            }
            return false;
          };
          for (const wire of document.querySelectorAll(".logic-circuit-wire")) {
            const points = parsePoints(wire.getAttribute("points"));
            const source = wire.dataset.source || "";
            const target = wire.dataset.target || "";
            const start = points[0];
            const end = points[points.length - 1];
            const sourceRect = nodeRects.get(source);
            const targetRect = nodeRects.get(target);
            const id = wire.dataset.wireId || `${source}->${target}`;
            if (!start || !end || !sourceRect || !targetRect) {
              failures.push(`${id}: missing endpoint or node`);
              continue;
            }
            if (!pointOnRectEdge(start, sourceRect) && !pointOnJunction(start, source)) {
              failures.push(`${id}: source endpoint floats`);
            }
            if (!pointOnRectEdge(end, targetRect) && !pointOnJunction(end, target)) {
              failures.push(`${id}: target endpoint floats`);
            }
            for (let index = 1; index < points.length; index += 1) {
              const a = points[index - 1];
              const b = points[index];
              for (const [nodeId, rect] of nodeRects) {
                if (nodeId === source || nodeId === target) continue;
                if (segmentCutsRect(a, b, rect)) {
                  failures.push(`${id}: segment ${index} cuts ${nodeId}`);
                }
              }
            }
          }
          const overflowingLabels = Array.from(document.querySelectorAll(
            ".logic-circuit-node-title, .logic-circuit-gate-label, .logic-circuit-node-subtitle, .logic-circuit-gate-caption"
          )).filter((label) => {
            const node = label.closest(".logic-circuit-node");
            const box = node?.querySelector(".logic-circuit-node-box, .logic-circuit-gate-box");
            const maxWidth = Number(box?.getAttribute("width") || 0) - 10;
            return maxWidth > 0
              && typeof label.getComputedTextLength === "function"
              && label.getComputedTextLength() > maxWidth + 1;
          }).map((label) => label.textContent || "");
          const stream = document.querySelector("#logic-drawing-stream-timeline");
          const streamBox = stream && !stream.hidden && stream.getClientRects().length
            ? stream.getBoundingClientRect()
            : null;
          const streamOverlaps = streamBox
            ? Array.from(document.querySelectorAll(".logic-circuit-node")).filter((node) => {
                const box = node.getBoundingClientRect();
                return !(streamBox.right < box.left
                  || streamBox.left > box.right
                  || streamBox.bottom < box.top
                  || streamBox.top > box.bottom);
              }).map((node) => node.dataset.demoNodeId || node.dataset.nodeId || "")
            : [];
          const wirePriority = (state) => {
            if (state === "fault" || state === "blocked") return 2;
            if (state === "active") return 1;
            return 0;
          };
          const paddedOverlap = (left, right, pad = 2) => (
            left.left - pad < right.right
            && left.right + pad > right.left
            && left.top - pad < right.bottom
            && left.bottom + pad > right.top
          );
          const renderedWires = Array.from(document.querySelectorAll(".logic-circuit-wire")).map((wire, index) => {
            const box = wire.getBoundingClientRect();
            return {
              index,
              id: wire.dataset.wireId || `${wire.dataset.source || ""}->${wire.dataset.target || ""}`,
              priority: wirePriority(wire.dataset.state || ""),
              box: {left: box.left, right: box.right, top: box.top, bottom: box.bottom},
            };
          });
          const wireOrderInversions = [];
          for (let leftIndex = 0; leftIndex < renderedWires.length; leftIndex += 1) {
            for (let rightIndex = leftIndex + 1; rightIndex < renderedWires.length; rightIndex += 1) {
              const left = renderedWires[leftIndex];
              const right = renderedWires[rightIndex];
              if (left.priority > right.priority && paddedOverlap(left.box, right.box)) {
                wireOrderInversions.push(`${left.id} renders before ${right.id}`);
              }
            }
          }
          return {failures, overflowingLabels, streamOverlaps, wireOrderInversions};
        }"""
    )
    assert geometry["failures"] == []
    assert geometry["overflowingLabels"] == []
    assert geometry["streamOverlaps"] == []
    assert geometry["wireOrderInversions"] == []


def _assert_sandbox_replay_blueprint_geometry(page: Any) -> None:
    geometry = page.evaluate(
        """() => {
          const canvas = document.querySelector("#fault-sandbox-replay-canvas-main");
          const canvasBox = canvas?.getBoundingClientRect();
          const failures = [];
          if (!canvas || !canvasBox) return {failures: ["missing replay canvas"], textOverflow: []};
          const nodeRects = new Map(Array.from(canvas.querySelectorAll("[data-replay-canvas-node]")).map((node) => {
            const box = node.getBoundingClientRect();
            return [node.dataset.replayCanvasNode || "", {
              left: box.left - canvasBox.left,
              right: box.right - canvasBox.left,
              top: box.top - canvasBox.top,
              bottom: box.bottom - canvasBox.top,
              width: box.width,
              height: box.height,
            }];
          }));
          const distanceToRectEdge = (point, rect) => {
            const clampedX = Math.max(rect.left, Math.min(point.x, rect.right));
            const clampedY = Math.max(rect.top, Math.min(point.y, rect.bottom));
            const inside = point.x >= rect.left && point.x <= rect.right && point.y >= rect.top && point.y <= rect.bottom;
            if (!inside) return Math.hypot(point.x - clampedX, point.y - clampedY);
            return Math.min(
              Math.abs(point.x - rect.left),
              Math.abs(point.x - rect.right),
              Math.abs(point.y - rect.top),
              Math.abs(point.y - rect.bottom),
            );
          };
          for (const link of canvas.querySelectorAll("[data-replay-canvas-link]")) {
            const source = link.dataset.sourceNode || "";
            const target = link.dataset.targetNode || "";
            const sourceRect = nodeRects.get(source);
            const targetRect = nodeRects.get(target);
            const start = {x: Number(link.dataset.startX), y: Number(link.dataset.startY)};
            const end = {x: Number(link.dataset.endX), y: Number(link.dataset.endY)};
            const id = link.dataset.replayCanvasLink || "link";
            if (!source || !target || !sourceRect || !targetRect || !Number.isFinite(start.x) || !Number.isFinite(end.x)) {
              failures.push(`${id}: missing source/target endpoint contract`);
              continue;
            }
            if (distanceToRectEdge(start, sourceRect) > 3.5) failures.push(`${id}: source endpoint floats`);
            if (distanceToRectEdge(end, targetRect) > 3.5) failures.push(`${id}: target endpoint floats`);
            if (Math.hypot(end.x - start.x, end.y - start.y) < 12) failures.push(`${id}: link too short`);
          }
          const linkBox = (id) => {
            const link = canvas.querySelector(`[data-replay-canvas-link="${id}"]`);
            if (!link) return null;
            const box = link.getBoundingClientRect();
            return {
              route: link.dataset.visualRoute || "",
              top: box.top - canvasBox.top,
              bottom: box.bottom - canvasBox.top,
              left: box.left - canvasBox.left,
              right: box.right - canvasBox.left,
            };
          };
          const latchCancel = linkBox("latch-cancel");
          const truthBoundary = linkBox("truth-boundary");
          const metricsBox = canvas.querySelector("#fault-sandbox-replay-canvas-metrics")?.getBoundingClientRect();
          if (!latchCancel || !truthBoundary) {
            failures.push("missing boundary lane links");
          } else {
            if (truthBoundary.route !== "elbow") failures.push("truth-boundary: missing elbow route");
            if (truthBoundary.top < latchCancel.bottom + 2) failures.push("truth-boundary: overlaps latch-cancel lane");
            if (metricsBox && truthBoundary.bottom > metricsBox.top - canvasBox.top - 4) {
              failures.push("truth-boundary: crowds metrics row");
            }
          }
          const textOverflow = Array.from(canvas.querySelectorAll(
            ".sandbox-replay-canvas-node strong, .sandbox-replay-canvas-node code, .sandbox-replay-canvas-metrics span"
          )).filter((element) => element.scrollWidth > element.clientWidth + 1)
            .map((element) => element.textContent || "");
          return {failures, textOverflow};
        }"""
    )
    assert geometry["failures"] == []
    assert geometry["textOverflow"] == []


def test_landing_page_defaults_to_five_entry_compact_shell(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="networkidle")
        expect(page.locator("#home-default-mode-grid")).to_be_visible()
        expect(page.locator("#home-default-mode-grid .home-mode-entry")).to_have_count(5)
        for label in ["画布", "运行", "参数", "证据", "报告"]:
            expect(page.locator("#home-default-mode-grid")).to_contain_text(label)
        expect(page.locator('#home-default-mode-grid a[href="/logic-builder"]')).to_be_visible()
        expect(page.locator('#home-default-mode-grid a[href="/logic-builder#run-drawer"]')).to_be_visible()
        expect(page.locator('#home-default-mode-grid a[href="/logic-builder#parameter-drawer"]')).to_be_visible()
        expect(page.locator('#home-default-mode-grid a[href="/logic-builder#evidence"]')).to_be_visible()
        expect(page.locator('#home-default-mode-grid a[href="/logic-builder#report"]')).to_be_visible()
        expect(page.locator(".home-command-palette-hint")).to_be_visible()
        expect(page.locator("#home-primary-flow-grid")).to_be_hidden()
        expect(page.locator("#deepseek-live-replay-import")).to_be_hidden()
        visible_text = page.locator("body").inner_text()
        for backstage_token in [
            "truth_effect",
            "candidate_state",
            "controller truth",
            "raw JSON",
            "artifacts/",
            "make demo-html",
            "demo.html 复刻",
        ]:
            assert backstage_token not in visible_text
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True
    finally:
        page.close()


def test_deepseek_subproject_nav_collapses_legacy_modules(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    try:
        page.goto(f"{demo_server}/logic-builder", wait_until="domcontentloaded")
        expect(page.locator("#deepseek-nav-mainline")).to_be_visible()
        _show_logic_builder_workbench(page)
        expect(page.locator("#deepseek-nav-mainline .unified-nav-link")).to_have_count(4)
        expect(page.locator('#deepseek-nav-mainline a[href="/requirements-intake"]')).to_be_visible()
        expect(page.locator('#deepseek-nav-mainline a[href="/logic-builder"]')).to_be_visible()
        expect(page.locator('#deepseek-nav-mainline a[href="/fault-injection-prepare"]')).to_be_visible()
        expect(page.locator('#deepseek-nav-mainline a[href="/fault-injection-sandbox"]')).to_be_visible()
        assert page.locator("#deepseek-nav-advanced-modules").evaluate("element => element.open") is False
        expect(page.locator('#deepseek-nav-advanced-modules a[href="/demo.html"]')).to_be_hidden()
        expect(page.locator('#deepseek-nav-advanced-modules a[href="/c919_etras_workstation.html"]')).to_be_hidden()
        expect(page.locator('#deepseek-nav-advanced-modules a[href="/fantui_requirements.html"]')).to_be_hidden()

        page.click("#deepseek-nav-advanced-modules summary")
        expect(page.locator('#deepseek-nav-advanced-modules a[href="/demo.html"]')).to_be_visible()
        expect(page.locator('#deepseek-nav-advanced-modules a[href="/fantui_circuit.html"]')).to_be_visible()
        expect(page.locator('#deepseek-nav-advanced-modules a[href="/c919_requirements.html"]')).to_be_visible()
        assert page.evaluate(
            """() => {
              const menu = document.querySelector("#deepseek-nav-advanced-modules .unified-nav-advanced-links");
              if (!menu) return false;
              const box = menu.getBoundingClientRect();
              const hit = document.elementFromPoint(box.left + 12, box.top + 12);
              return Boolean(hit && menu.contains(hit));
            }"""
        ) is True
    finally:
        page.close()


def test_deepseek_four_page_command_strips_use_single_primary_next_cta(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page_contracts = [
        (
            "/requirements-intake",
            "1",
            "STEP 1/4",
            "需求理解",
            "#logic-builder-next",
            "下一步：进入逻辑链路绘制",
            '[data-usage-path-cue="requirements"]',
            "下一页生成逻辑画布",
            [("#requirements-analyze", re.compile(r"^检查：(分析需求|本地预解析)$"))],
        ),
        (
            "/logic-builder",
            "2",
            "第 2/4 步",
            "逻辑复制",
            "#logic-fault-next",
            "下一步：进入故障准备",
            '[data-usage-path-cue="logic"]',
            "下一页生成故障矩阵",
            [
                ("#logic-regenerate", "检查：重新绘制"),
                ("#logic-back", "更多：返回需求"),
            ],
        ),
        (
            "/fault-injection-prepare",
            "3",
            "第 3/4 步",
            "故障准备",
            "#fault-sandbox-next",
            "下一步：进入沙盒审查",
            '[data-usage-path-cue="fault"]',
            "候选矩阵",
            [
                ("#fault-generate", "检查：生成候选"),
                ("#fault-back", "更多：返回逻辑复制"),
            ],
        ),
        (
            "/fault-injection-sandbox",
            "4",
            "第 4/4 步",
            "沙盒审查",
            "#fault-sandbox-revision-next",
            "下一步：生成逻辑修订单",
            '[data-usage-path-cue="sandbox"]',
            "生成修订单",
            [
                ("#fault-sandbox-generate", "检查：生成配置"),
                ("#fault-sandbox-back", "更多：返回故障准备"),
            ],
        ),
    ]
    try:
        for path, step, step_label, title, primary_selector, primary_text, cue_selector, cue_text, secondary_buttons in page_contracts:
            page.goto(f"{demo_server}{path}", wait_until="networkidle")
            strip = page.locator('[data-command-strip="deepseek-step"]')
            if path == "/logic-builder":
                expect(strip).to_be_visible()
                _show_logic_builder_workbench(page)
            expect(strip).to_be_visible()
            expect(strip).to_have_attribute("data-command-step", step)
            expect(strip.locator("h1")).to_have_text(title)
            expect(strip.locator(".deepseek-step-kicker")).to_have_text(step_label)
            expect(page.locator(cue_selector)).to_be_visible()
            expect(page.locator(cue_selector)).to_contain_text(cue_text)
            expect(strip.locator('[data-primary-next-action="true"]')).to_have_count(1)
            expect(strip.locator(primary_selector)).to_have_text(primary_text)
            expect(strip.locator(primary_selector)).to_have_attribute("data-primary-next-action", "true")
            for selector, text in secondary_buttons:
                expect(strip.locator(selector)).to_have_text(text)
                assert "secondary" in (strip.locator(selector).get_attribute("class") or "")
            box = strip.bounding_box()
            assert box is not None
            assert box["height"] <= 128
    finally:
        page.close()


def test_deepseek_low_cognitive_load_guardrails_hold_in_browser(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page_contracts = [
        (
            "/requirements-intake",
            "#requirements-workflow-steps",
            "#logic-builder-next",
            {
                "#requirements-analyze": "secondary",
                "#requirements-replay-import": "secondary",
                "#requirements-offline-action": "secondary",
                "#requirements-clear": "advanced",
            },
        ),
        (
            "/logic-builder",
            "#logic-workflow-steps",
            "#logic-fault-next",
            {
                "#logic-regenerate": "secondary",
                "#logic-back": "secondary",
                "#logic-fill-handoff-draft": "secondary",
                "#logic-clear-change": "advanced",
                "#logic-cancel-change": "advanced",
            },
        ),
        (
            "/fault-injection-prepare",
            "#fault-workflow-steps",
            "#fault-sandbox-next",
            {
                "#fault-generate": "secondary",
                "#fault-back": "secondary",
                "#fault-save-boundaries": "secondary",
            },
        ),
        (
            "/fault-injection-sandbox",
            "#fault-sandbox-workflow-steps",
            "#fault-sandbox-revision-next",
            {
                "#fault-sandbox-generate": "secondary",
                "#fault-sandbox-back": "secondary",
            },
        ),
    ]
    try:
        for path, workflow_selector, primary_selector, button_tiers in page_contracts:
            page.goto(f"{demo_server}{path}", wait_until="networkidle")
            if path == "/logic-builder":
                _show_logic_builder_workbench(page)
            expect(page.locator("#deepseek-nav-mainline")).to_have_attribute("data-ux-main-flow", "four-step")
            expect(page.locator("#deepseek-nav-mainline .unified-nav-link")).to_have_count(4)
            expect(page.locator("#deepseek-nav-advanced-modules")).not_to_have_attribute("open", "")
            expect(page.locator(workflow_selector)).to_have_attribute("data-ux-main-flow", "four-step")
            expect(page.locator('[data-primary-next-action="true"]')).to_have_count(1)
            expect(page.locator(primary_selector)).to_have_attribute("data-ux-action-tier", "primary")

            for selector, tier in button_tiers.items():
                expect(page.locator(selector)).to_have_attribute("data-ux-action-tier", tier)

            mispromoted_tools = page.evaluate(
                """() => {
                  const riskText = /清空|取消|返回|重新|重绘|回放|本地|保存|生成修改意见草稿/;
                  return Array.from(document.querySelectorAll("button"))
                    .filter((button) => {
                      const box = button.getBoundingClientRect();
                      return box.width > 0 && box.height > 0 && riskText.test(button.textContent || "");
                    })
                    .filter((button) => {
                      const tier = button.dataset.uxActionTier;
                      return button.dataset.primaryNextAction === "true" || !["secondary", "advanced"].includes(tier);
                    })
                    .map((button) => `${button.id || button.textContent}:${button.dataset.uxActionTier || "missing"}`);
                }"""
            )
            assert mispromoted_tools == []

        page.goto(f"{demo_server}/demo-reconstruction", wait_until="networkidle")
        expect(page.locator("body")).to_have_attribute("data-ux-page-role", "demo-mvp-console")
        expect(page.locator('[data-primary-next-action="true"]')).to_have_count(0)
        expect(page.locator("#demo-reconstruction-console-frame")).to_be_visible()
        expect(page.locator("#demo-reconstruction-browser-evidence")).to_be_visible()
    finally:
        page.close()


def test_requirements_intake_compacts_first_run_decision_board(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    try:
        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        board = page.locator('[data-decision-board="requirements"]')
        expect(board).to_be_visible()
        expect(board.locator(".requirements-decision-card")).to_have_count(3)
        expect(board.locator('[data-decision-card="path"] h2')).to_have_text("路径")
        expect(board.locator('[data-decision-card="verdict"] h2')).to_have_text("当前结论")
        expect(board.locator('[data-decision-card="next"] h2')).to_have_text("下一步")
        expect(board.locator("#requirements-preflight-live-state")).to_be_visible()
        expect(board.locator("#requirements-replay-import")).to_have_text("回放")
        expect(board.locator("#requirements-offline-action")).to_have_text("本地")
        expect(board.locator("#result-state")).to_have_text("尚未生成")
        expect(board.locator("#requirements-summary")).to_contain_text("等待模型")
        expect(board.locator("#next-step-copy")).to_contain_text("先上传需求")
        expect(board.locator('[data-usage-path-cue="requirements"]')).to_contain_text("下一页生成逻辑画布")
        expect(board.locator("#requirements-burden-action")).to_have_text("等待分析")
        expect(page.locator(".requirements-result-panel .result-header")).to_have_count(0)
        expect(page.locator(".requirements-result-panel #next-step-panel")).to_have_count(0)
        expect(page.locator(".requirements-result-panel #requirements-burden-summary")).to_have_count(0)

        board_box = board.bounding_box()
        layout_box = page.locator(".requirements-layout").bounding_box()
        assert board_box is not None
        assert layout_box is not None
        assert board_box["height"] <= 180
        assert layout_box["y"] <= 500
    finally:
        page.close()


def test_desktop_requirements_preflight_uses_compact_status_copy(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 820})
    try:
        page.route("**/api/requirements-intake/provider-status?provider=deepseek", lambda route: _fulfill_json(route, {
            "provider": "deepseek",
            "model": "deepseek-v4-pro",
            "api_base": "https://api.deepseek.com",
            "key_available": False,
            "key_source": "",
            "live_ready": False,
            "checked": ["DEEPSEEK_API_KEY", "DeepSeek_API_key"],
        }))

        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        board = page.locator('[data-decision-board="requirements"]')
        expect(board.locator('[data-decision-card="path"] h2')).to_have_text("路径")
        expect(board.locator("#requirements-preflight-live-card > span")).to_have_text("DeepSeek")
        expect(board.locator("#requirements-preflight-live-state")).to_have_text("未接入")
        expect(board.locator("#requirements-preflight-replay-state")).to_have_text("回放可用")
        expect(board.locator("#requirements-preflight-offline-state")).to_have_text("本地候选")
        expect(page.locator(".requirements-live-only-row span")).to_have_text("仅 DeepSeek")
        expect(page.locator("#requirements-provider-key-source")).to_have_text("env key 缺失")

        board_box = board.bounding_box()
        assert board_box is not None
        assert board_box["height"] <= 150
        assert "DEEPSEEK_API_KEY" not in (board.inner_text() + page.locator("#requirements-provider-key-source").inner_text())
    finally:
        page.close()


def test_desktop_requirements_page_draws_demo_cockpit_skin(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    try:
        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        cockpit = page.locator('[data-ui-skin="demo-cockpit"]')
        expect(cockpit).to_be_visible()
        expect(page.locator('[data-cockpit-role="canopy-frame"]')).to_be_visible()
        expect(page.locator('[data-cockpit-role="status-banner"]')).to_be_visible()
        expect(page.locator('[data-cockpit-role="instrument-rail"]')).to_be_visible()
        expect(page.locator('[data-cockpit-role="input-bay"]')).to_be_visible()
        expect(page.locator('[data-cockpit-role="mission-console"]')).to_be_visible()
        expect(page.locator('[data-cockpit-role="mission-strip"]')).to_be_hidden()

        expect(page.locator(".requirements-cockpit-canopy-window")).to_have_count(3)
        expect(page.locator('[data-cockpit-role="instrument-rail"] .requirements-decision-card')).to_have_count(3)
        expect(page.locator('[data-cockpit-role="mission-console"] .clarification-primary')).to_be_visible()

        cockpit_box = cockpit.bounding_box()
        rail_box = page.locator('[data-cockpit-role="instrument-rail"]').bounding_box()
        console_box = page.locator('[data-cockpit-role="mission-console"]').bounding_box()
        assert cockpit_box is not None
        assert rail_box is not None
        assert console_box is not None
        assert cockpit_box["width"] >= 1320
        assert rail_box["y"] < console_box["y"]
    finally:
        page.close()


def test_desktop_requirements_workbench_prioritizes_clarification_over_secondary_outputs(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    try:
        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        layout = page.locator(".requirements-layout")
        shell = page.locator(".requirements-shell")
        expect(shell).to_have_attribute("data-workstation-shell", "canvas-first")
        expect(shell).to_have_attribute("data-workstation-state", "primary")
        expect(shell).to_have_attribute("data-blueprint14-rhythm", "compact-canvas")
        expect(shell).to_have_attribute("data-active-aux-panel", "none")
        expect(shell).to_have_attribute("data-unified-inspector-state", "none")
        expect(page.locator('[data-blueprint14-compact-topbar="step-provider-next"]')).to_be_visible()
        expect(page.locator('#requirements-preflight-panel[data-blueprint14-density="compact-decision-board"]')).to_be_visible()
        expect(layout).to_have_attribute("data-desktop-workbench", "input-clarification")
        expect(layout).to_have_attribute("data-workstation-layout", "primary-canvas-plus-inspector")
        expect(layout).to_have_attribute("data-blueprint14-layout", "source-inspector-primary-canvas")
        expect(page.locator(".requirements-input-panel")).to_be_visible()
        expect(page.locator('.requirements-input-panel[data-workstation-inspector="source-input"]')).to_be_visible()
        expect(page.locator('.requirements-input-panel[data-blueprint14-inspector="source-document-input"]')).to_be_visible()
        expect(page.locator(".clarification-primary")).to_be_visible()
        expect(page.locator('.clarification-primary[data-workstation-stage="primary-canvas"]')).to_be_visible()
        expect(page.locator('.clarification-primary[data-blueprint14-canvas-rhythm="expanded-first-screen"]')).to_be_visible()
        expect(page.locator("#requirements-secondary-panels > details")).to_have_count(4)

        for selector in [
            "#clarification-trace",
            "#requirements-questions-panel",
            "#requirements-concept-graph-panel",
            "#requirements-edges-panel",
        ]:
            assert page.locator(selector).evaluate(
                "element => element.tagName.toLowerCase() === 'details' && !element.open"
            )

        expect(page.locator("#requirements-graph")).not_to_be_visible()
        expect(page.locator("#requirements-edges")).not_to_be_visible()

        input_box = page.locator(".requirements-input-panel").bounding_box()
        primary_box = page.locator(".clarification-primary").bounding_box()
        assert input_box is not None
        assert primary_box is not None
        assert primary_box["x"] > input_box["x"] + input_box["width"] - 1
        assert primary_box["width"] >= 650
        assert primary_box["height"] >= 240
        assert abs(primary_box["y"] - input_box["y"]) <= 14
        expect(page.locator("#requirements-secondary-panels")).to_be_hidden()

        page.locator('[data-requirement-choice-row="l1"]').click()
        expect(shell).to_have_attribute("data-active-aux-panel", "source-popover")
        expect(shell).to_have_attribute("data-unified-inspector-state", "source-popover")
        expect(page.locator("#requirements-row-popover")).to_be_visible()
        expect(page.locator("#requirements-row-popover")).to_have_attribute("data-unified-panel-state", "open")

        page.click("#requirements-manual-toggle")
        expect(shell).to_have_attribute("data-active-aux-panel", "manual-bubble")
        expect(shell).to_have_attribute("data-unified-inspector-state", "manual-bubble")
        expect(page.locator("#requirements-row-popover")).to_be_hidden()
        expect(page.locator("#requirements-row-popover")).to_have_attribute("data-unified-panel-state", "closed")
        expect(page.locator("#requirements-manual-bubble")).to_have_attribute("data-unified-panel-state", "open")

        page.keyboard.press("Escape")
        expect(shell).to_have_attribute("data-active-aux-panel", "none")
        expect(shell).to_have_attribute("data-workstation-state", "primary")
        expect(page.locator("#requirements-manual-bubble")).to_be_hidden()
        expect(page.locator("#requirements-manual-bubble")).to_have_attribute("data-unified-panel-state", "closed")
    finally:
        page.close()


def test_fault_sandbox_review_uses_three_primary_gates_for_dense_plan(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )
        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="networkidle")
        expect(page.locator("#fault-sandbox-result-state")).to_have_text("配置已生成")
        expect(page.locator("#fault-sandbox-plan-count")).to_have_text("9 计划")
        expect(page.locator("#fault-sandbox-observation-count")).to_have_text("9 观测点")
        expect(page.locator("#fault-sandbox-review-count")).to_have_text("8 审查项")
        expect(page.locator("#fault-sandbox-review-row-panel")).to_be_visible()
        expect(page.locator("#fault-sandbox-review-row-count")).to_have_text("7 行")
        expect(page.locator("#fault-sandbox-review-rows[data-blueprint-density='compact-workbench']")).to_be_visible()
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row-header")).to_be_visible()
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows .blueprint-row--sandbox-review")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows .blueprint-density-row")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint-row-pattern='shared-v1']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint-review-row]")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint36-row='sandbox-review']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint-density='compact-workbench']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint36-row='sandbox-review'] [data-blueprint-col='trace-report']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row-decision")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row-link-token")).to_have_count(14)
        assert page.locator("#fault-sandbox-review-rows .blueprint-row-token").count() >= 21
        expect(page.locator("[data-blueprint-review-row='SR-06'] [data-link-kind='trace']")).to_have_text("ET-04")
        expect(page.locator("[data-blueprint-review-row='SR-06'] [data-link-kind='report']")).to_have_text("RP-06")
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row-check input[disabled]")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows")).to_contain_text("控制真相未修改")
        sr07_description = page.locator("[data-blueprint-review-row='SR-07'] .sandbox-review-row-description-text")
        for boundary in ["truth_effect:none", "certification_claim:none", "controller_truth_modified:false"]:
            expect(sr07_description.locator(f'[data-boundary-token="{boundary}"]')).to_have_count(1)
            assert boundary not in sr07_description.inner_text()
        review_row_box = page.locator("#fault-sandbox-review-rows [data-blueprint-density='compact-workbench']").first.bounding_box()
        assert review_row_box
        assert review_row_box["height"] >= 52
        assert review_row_box["height"] <= 58
        review_rows_box = page.locator("#fault-sandbox-review-rows").bounding_box()
        report_strip_box = page.locator("#sandbox-report-strip").bounding_box()
        assert review_rows_box and report_strip_box
        assert review_rows_box["height"] > 400
        assert review_rows_box["y"] + review_rows_box["height"] <= report_strip_box["y"] - 12
        review_row_bottoms = page.locator("#fault-sandbox-review-rows .sandbox-review-row").evaluate_all(
            "nodes => nodes.map((node) => node.getBoundingClientRect().bottom)"
        )
        assert report_strip_box["y"] - max(review_row_bottoms) <= 72
        assert page.locator("#fault-sandbox-review-rows").evaluate(
            "node => node.scrollHeight <= node.clientHeight + 1"
        ) is True
        expect(page.locator("#fault-sandbox-diagnosis-inspector")).to_be_visible()
        expect(page.locator("#fault-sandbox-diagnosis-summary")).to_contain_text("空跑")
        expect(page.locator("#fault-sandbox-affected-path")).to_have_text("node 1 -> node 1")
        expect(page.locator("#fault-sandbox-first-abnormal-node")).to_have_text("node 1")
        expect(page.locator("#fault-sandbox-diagnosis-chain [data-blueprint36-chain-node='failure-path']")).to_have_count(3)
        expect(page.locator("#fault-sandbox-diagnosis-chain .blueprint-row--diagnosis-chain")).to_have_count(3)
        expect(page.locator("#fault-sandbox-diagnosis-chain [data-blueprint-row-pattern='shared-v1']")).to_have_count(3)
        expect(page.locator("#fault-sandbox-diagnosis-chain .sandbox-diagnosis-chain-link-token")).to_have_count(6)
        expect(page.locator("#fault-sandbox-diagnosis-evidence-links [data-blueprint36-evidence-link='diagnosis']")).to_have_count(3)
        expect(page.locator("#fault-sandbox-repair-suggestions")).to_contain_text("修订单")
        expect(page.locator("#fault-sandbox-evidence-trace")).to_be_visible()
        expect(page.locator("#fault-sandbox-evidence-trace-rows .sandbox-evidence-trace-row")).to_have_count(4)
        expect(page.locator("#fault-sandbox-evidence-trace-rows .blueprint-row--evidence-chain")).to_have_count(4)
        expect(page.locator("#fault-sandbox-evidence-trace-rows [data-blueprint36-evidence-row='evidence-chain']")).to_have_count(4)
        expect(page.locator("#fault-sandbox-evidence-trace-rows [data-blueprint-row-pattern='shared-v1']")).to_have_count(4)
        expect(page.locator("#fault-sandbox-evidence-trace-rows .sandbox-evidence-trace-link-token")).to_have_count(8)
        expect(page.locator("[data-evidence-trace-id='ET-04'] [data-link-kind='report']")).to_have_text("RP-06")
        expect(page.locator("#fault-sandbox-evidence-trace-rows")).to_contain_text("审查行")
        expect(page.locator("#fault-sandbox-report-preview")).to_be_visible()
        expect(page.locator("#fault-sandbox-report-section-rows .sandbox-report-section-row")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows .blueprint-row--replay-report")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint-report-row='review-package-section']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint36-report-row='replay-report']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint-row-pattern='shared-v1']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows .sandbox-report-section-decision")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows .sandbox-report-link-token")).to_have_count(14)
        expect(page.locator("[data-report-section-id='RP-06'] [data-link-kind='trace']")).to_have_text("ET-04")
        expect(page.locator("[data-report-section-id='RP-06'] [data-link-kind='report']")).to_have_text("RP-06")
        expect(page.locator("#fault-sandbox-report-section-rows")).to_contain_text("故障覆盖")
        page.locator('[data-blueprint-review-row="SR-06"]').press("Enter")
        expect(page.locator('[data-blueprint-review-row="SR-06"]')).to_have_class(re.compile("is-active"))
        expect(page.locator('[data-blueprint-review-row="SR-06"]')).to_have_attribute("aria-selected", "true")
        expect(page.locator("#fault-sandbox-diagnosis-inspector")).to_have_attribute("data-active-review-row", "SR-06")
        expect(page.locator('[data-evidence-trace-id="ET-04"]')).to_have_class(re.compile("is-linked-active"))
        expect(page.locator('[data-report-section-id="RP-06"]')).to_have_class(re.compile("is-linked-active"))
        expect(page.locator("#sandbox-evidence-title")).to_contain_text("报告可追溯")
        expect(page.locator("#sandbox-evidence-body")).to_contain_text("对应报告章节")
        expect(page.locator("#sandbox-evidence-body")).to_contain_text("RP-06")
        page.locator("#sandbox-evidence-close").click()
        page.locator('[data-blueprint-review-row="SR-07"]').press("Enter")
        expect(page.locator('[data-blueprint-review-row="SR-07"]')).to_have_attribute("aria-selected", "true")
        expect(page.locator("[data-blueprint-review-row='SR-07'] .sandbox-review-row-decision")).to_have_text(re.compile("通过|待复核|等待"))
        expect(page.locator('[data-report-section-id="RP-07"]')).to_have_class(re.compile("is-linked-active"))
        expect(page.locator("#sandbox-evidence-title")).to_contain_text("控制真相未修改")
        page.locator("#sandbox-evidence-close").click()
        page.locator('[data-evidence-trace-id="ET-03"]').click()
        expect(page.locator("#sandbox-evidence-popover")).to_be_visible()
        evidence_body = page.locator("#sandbox-evidence-body")
        expect(evidence_body).to_contain_text("RP-07")
        expect(evidence_body.locator('#sandbox-evidence-link-summary [data-boundary-token="truth_effect:none"]')).to_have_count(1)
        expect(evidence_body.locator('dl [data-boundary-token="truth_effect:none"]')).to_have_count(1)
        expect(evidence_body.locator('dl [data-boundary-token="certification_claim:none"]')).to_have_count(1)
        page.locator("#sandbox-evidence-close").click()
        page.locator('[data-sandbox-report-action="export"]').click()
        expect(page.locator("#sandbox-evidence-popover")).to_be_hidden()
        expect(page.locator("#sandbox-review-package-panel")).to_be_visible()
        expect(page.locator("#sandbox-review-package-review-count")).to_have_text("7 审查行")
        expect(page.locator("#sandbox-review-package-evidence-count")).to_have_text("4 证据回链")
        expect(page.locator("#sandbox-review-package-report-count")).to_have_text("7 报告章节")
        expect(page.locator("#sandbox-review-package-review-rows [data-package-item-id^='SR-']")).to_have_count(7)
        expect(page.locator("#sandbox-review-package-evidence-rows [data-package-item-id^='ET-']")).to_have_count(4)
        expect(page.locator("#sandbox-review-package-report-rows [data-package-item-id^='RP-']")).to_have_count(7)
        expect(page.locator("#sandbox-review-package-panel .blueprint-row--review-package")).to_have_count(18)
        expect(page.locator("#sandbox-review-package-panel [data-blueprint-row-pattern='shared-v1']")).to_have_count(18)
        expect(page.locator("#sandbox-review-package-review-rows [data-blueprint36-package-row='review-package-review']")).to_have_count(7)
        expect(page.locator("#sandbox-review-package-report-rows [data-blueprint36-package-row='review-package-report']")).to_have_count(7)
        expect(page.locator("#sandbox-review-package-review-rows [data-blueprint36-package-row='review-package-review'] .sandbox-review-package-link-token")).to_have_count(14)
        expect(page.locator("#sandbox-review-package-report-rows [data-blueprint36-package-row='review-package-report'] .sandbox-review-package-link-token")).to_have_count(14)
        expect(page.locator('#sandbox-review-package-invariants [data-boundary-token="truth_effect:none"]')).to_have_count(1)
        review_package_row = page.locator("#sandbox-review-package-review-rows [data-package-item-id='SR-04']")
        expect(review_package_row).to_have_attribute("data-package-target-trace-id", "ET-02")
        expect(review_package_row).to_have_attribute("data-package-target-report-id", "RP-05")
        expect(review_package_row.locator("[data-link-kind='trace']")).to_have_text("ET-02")
        expect(review_package_row.locator("[data-link-kind='report']")).to_have_text("RP-05")
        review_package_row.click()
        expect(page.locator("#sandbox-review-package-panel")).to_be_hidden()
        expect(page.locator('[data-blueprint-review-row="SR-04"]')).to_have_attribute("aria-selected", "true")
        expect(page.locator('[data-evidence-trace-id="ET-02"]')).to_have_class(re.compile("is-linked-active"))
        expect(page.locator('[data-report-section-id="RP-05"]')).to_have_class(re.compile("is-linked-active"))
        expect(page.locator("#sandbox-evidence-title")).to_contain_text("故障覆盖")
        page.locator("#sandbox-evidence-close").click()

        page.locator('[data-sandbox-report-action="export"]').click()
        evidence_package_row = page.locator("#sandbox-review-package-evidence-rows [data-package-item-id='ET-04']")
        expect(evidence_package_row).to_have_attribute("data-package-target-review-row", "SR-06")
        expect(evidence_package_row.locator(".sandbox-review-package-decision")).to_have_text("证据回链")
        evidence_package_row.click()
        expect(page.locator("#sandbox-review-package-panel")).to_be_hidden()
        expect(page.locator('[data-blueprint-review-row="SR-06"]')).to_have_attribute("aria-selected", "true")
        expect(page.locator('[data-evidence-trace-id="ET-04"]')).to_have_class(re.compile("is-linked-active"))
        expect(page.locator('[data-report-section-id="RP-06"]')).to_have_class(re.compile("is-linked-active"))
        expect(page.locator("#sandbox-evidence-title")).to_contain_text("报告可追溯")
        page.locator("#sandbox-evidence-close").click()

        page.locator('[data-sandbox-report-action="export"]').click()
        report_package_row = page.locator("#sandbox-review-package-report-rows [data-package-item-id='RP-07']")
        expect(report_package_row).to_have_attribute("data-package-target-review-row", "SR-07")
        expect(report_package_row).to_have_attribute("data-package-target-trace-id", "ET-03")
        expect(report_package_row.locator(".sandbox-review-package-decision")).to_have_text(re.compile("通过|待复核|等待"))
        expect(report_package_row.locator("[data-link-kind='trace']")).to_have_text("ET-03")
        expect(report_package_row.locator("[data-link-kind='report']")).to_have_text("RP-07")
        report_package_row.press("Enter")
        expect(page.locator("#sandbox-review-package-panel")).to_be_hidden()
        expect(page.locator('[data-blueprint-review-row="SR-07"]')).to_have_attribute("aria-selected", "true")
        expect(page.locator('[data-report-section-id="RP-07"]')).to_have_class(re.compile("is-linked-active"))
        expect(page.locator("#sandbox-evidence-title")).to_contain_text("控制真相未修改")
        page.locator("#sandbox-evidence-close").click()

        page.locator('[data-sandbox-report-action="export"]').click()
        expect(page.locator("#sandbox-review-package-panel")).to_be_visible()
        page.keyboard.press("Escape")
        expect(page.locator("#sandbox-review-package-panel")).to_be_hidden()
        expect(page.locator("#fault-sandbox-primary-gates")).to_be_visible()
        expect(page.locator("#fault-sandbox-detail-groups")).to_be_hidden()
        expect(page.locator("input[data-sandbox-confirm]")).to_have_count(3)
        expect(page.locator("#fault-sandbox-review-gate")).to_have_text("需确认 3 个一级闸门")
        assert page.locator("#fault-sandbox-detail-groups details").first.evaluate("element => element.open") is False

        page.locator('input[data-sandbox-confirm="dry-run"]').check()
        expect(page.locator("#fault-sandbox-review-gate")).to_have_text("已确认 1/3 个一级闸门")
        page.locator('input[data-sandbox-confirm="coverage"]').check()
        page.locator('input[data-sandbox-confirm="risk"]').check()
        expect(page.locator("#fault-sandbox-review-gate")).to_have_text("可进入逻辑修订")
    finally:
        page.close()


def test_fault_sandbox_unified_inspector_summary_tracks_review_evidence_and_report(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    model_calls: list[str] = []
    tick_calls: list[str] = []
    try:
        def reject_model_call(route: Any) -> None:
            model_calls.append(route.request.url)
            route.fulfill(status=500, content_type="application/json", body='{"error":"model_call_forbidden"}')

        page.route("**/api/requirements-intake/prepare-fault-injection/sandbox", reject_model_call)
        page.route("**/api/tick", lambda route: (tick_calls.append(route.request.url), route.abort()))
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )

        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="networkidle")
        page.locator('[data-blueprint-review-row="SR-06"]').press("Enter")
        inspector_summary = page.locator("#sandbox-evidence-link-summary")
        expect(inspector_summary).to_be_visible()
        expect(inspector_summary).to_have_attribute("data-active-review-row", "SR-06")
        expect(inspector_summary).to_have_attribute("data-active-trace-id", "ET-04")
        expect(inspector_summary).to_have_attribute("data-active-report-id", "RP-06")
        expect(inspector_summary).to_have_attribute("data-inspector-source", "review-row")
        expect(inspector_summary).to_contain_text("SR-06")
        expect(inspector_summary).to_contain_text("ET-04")
        expect(inspector_summary).to_contain_text("RP-06")
        for boundary in ["truth_effect:none", "controller_truth_modified:false"]:
            expect(inspector_summary.locator(f'[data-boundary-token="{boundary}"]')).to_have_count(1)

        page.locator('[data-blueprint-review-row="SR-07"]').press("Enter")
        expect(inspector_summary).to_have_attribute("data-active-review-row", "SR-07")
        expect(inspector_summary).to_have_attribute("data-active-trace-id", "ET-03")
        expect(inspector_summary).to_have_attribute("data-active-report-id", "RP-07")

        page.locator('[data-blueprint-review-row="SR-06"]').press("Enter")
        page.locator('[data-evidence-trace-id="ET-04"]').press("Enter")
        expect(inspector_summary).to_have_attribute("data-inspector-source", "evidence-trace")
        expect(inspector_summary).to_have_attribute("data-active-review-row", "SR-06")
        expect(inspector_summary).to_have_attribute("data-active-trace-id", "ET-04")
        expect(inspector_summary).to_have_attribute("data-active-report-id", "RP-06")
        expect(page.locator('[data-blueprint-review-row="SR-06"]')).to_have_attribute("aria-selected", "true")
        expect(page.locator('[data-report-section-id="RP-06"]')).to_have_class(re.compile("is-linked-active"))

        page.locator('[data-report-section-id="RP-07"]').press("Enter")
        expect(inspector_summary).to_have_attribute("data-inspector-source", "replay-report")
        expect(inspector_summary).to_have_attribute("data-active-review-row", "SR-07")
        expect(inspector_summary).to_have_attribute("data-active-trace-id", "ET-03")
        expect(inspector_summary).to_have_attribute("data-active-report-id", "RP-07")
        expect(page.locator('[data-blueprint-review-row="SR-07"]')).to_have_attribute("aria-selected", "true")
        expect(page.locator('[data-evidence-trace-id="ET-03"]')).to_have_class(re.compile("is-linked-active"))

        page.locator("#sandbox-evidence-close").click()
        page.locator('[data-sandbox-report-action="export"]').click()
        page.locator("#sandbox-review-package-evidence-rows [data-package-item-id='ET-04']").click()
        expect(inspector_summary).to_be_visible()
        expect(inspector_summary).to_have_attribute("data-inspector-source", "review-package")
        expect(inspector_summary).to_have_attribute("data-active-review-row", "SR-06")
        expect(inspector_summary).to_have_attribute("data-active-trace-id", "ET-04")
        expect(inspector_summary).to_have_attribute("data-active-report-id", "RP-06")
        expect(page.locator("#sandbox-review-package-panel")).to_be_hidden()
        assert model_calls == []
        assert tick_calls == []
    finally:
        page.close()


def test_fault_sandbox_review_rows_remain_pointer_clickable_above_report_strip(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )
        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="networkidle")

        review_rows = page.locator("#fault-sandbox-review-rows")
        first_review_row = review_rows.locator(".sandbox-review-row").first
        report_strip = page.locator("#sandbox-report-strip")
        expect(report_strip).to_be_visible()
        review_rows_box = review_rows.bounding_box()
        first_review_row_box = first_review_row.bounding_box()
        report_strip_box = report_strip.bounding_box()
        assert review_rows_box and first_review_row_box and report_strip_box
        assert review_rows_box["height"] >= 168
        assert review_rows_box["y"] < report_strip_box["y"]
        assert review_rows_box["y"] + review_rows_box["height"] <= report_strip_box["y"] - 12
        assert first_review_row_box["y"] + first_review_row_box["height"] <= report_strip_box["y"] - 32
        fully_visible_review_rows = review_rows.locator(".sandbox-review-row").evaluate_all(
            """(nodes, bounds) => nodes.filter((node) => {
              const row = node.getBoundingClientRect();
              return row.y >= bounds.listY - 1
                && row.y + row.height <= Math.min(bounds.listBottom, bounds.stripY) + 1;
            }).map((node) => node.dataset.blueprintReviewRow)""",
            {
                "listY": review_rows_box["y"],
                "listBottom": review_rows_box["y"] + review_rows_box["height"],
                "stripY": report_strip_box["y"],
            },
        )
        assert fully_visible_review_rows == ["SR-01", "SR-02", "SR-03", "SR-04", "SR-05", "SR-06", "SR-07"]
        clipped_review_rows = review_rows.locator(".sandbox-review-row").evaluate_all(
            """(nodes) => nodes.map((node) => ({
              id: node.dataset.blueprintReviewRow,
              clientHeight: node.clientHeight,
              scrollHeight: node.scrollHeight,
            })).filter((row) => row.scrollHeight > row.clientHeight + 1)"""
        )
        assert clipped_review_rows == []

        target_row = page.locator('[data-blueprint-review-row="SR-06"]')
        expect(target_row).to_be_visible()
        target_row.click()
        inspector_summary = page.locator("#sandbox-evidence-link-summary")
        expect(inspector_summary).to_be_visible()
        expect(inspector_summary).to_have_attribute("data-active-review-row", "SR-06")
        expect(inspector_summary).to_have_attribute("data-active-trace-id", "ET-04")
        expect(inspector_summary).to_have_attribute("data-active-report-id", "RP-06")
        page.locator("#sandbox-evidence-close").click()
        page.locator('[data-sandbox-report-action="export"]').click()
        expect(page.locator("#sandbox-review-package-panel")).to_be_visible()
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True
        assert page.evaluate("() => document.scrollingElement.scrollWidth <= window.innerWidth") is True
    finally:
        page.close()


def test_fault_sandbox_report_strip_prioritizes_review_package_action(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )
        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="networkidle")

        report_strip = page.locator("#sandbox-report-strip")
        expect(report_strip).to_be_visible()
        export_action = report_strip.locator('[data-sandbox-report-action="export"]')
        expect(export_action).to_be_visible()
        expect(export_action).to_have_attribute("data-ux-action-tier", "primary")
        expect(export_action).to_have_attribute("data-report-primary-action", "review-package")
        expect(export_action).to_have_class(re.compile("sandbox-report-primary"))

        assert report_strip.locator('[data-ux-action-tier="primary"]').count() == 1
        for action_id in ["rerun", "evidence", "revision"]:
            secondary_action = report_strip.locator(f'[data-sandbox-report-action="{action_id}"]')
            expect(secondary_action).to_be_visible()
            expect(secondary_action).to_have_attribute("data-ux-action-tier", "secondary")
            expect(secondary_action).to_have_class(re.compile("sandbox-report-secondary"))

        for boundary in [
            "sandbox_candidate",
            "truth_effect:none",
            "certification_claim:none",
            "controller_truth_modified:false",
        ]:
            expect(report_strip.locator(f'[data-boundary-token="{boundary}"]')).to_have_count(1)

        assert report_strip.evaluate("(element) => element.getBoundingClientRect().height <= 132") is True
        export_action.click()
        expect(page.locator("#sandbox-review-package-panel")).to_be_visible()
        review_package_rows_box = page.locator("#sandbox-review-package-review-rows").bounding_box()
        evidence_package_rows_box = page.locator("#sandbox-review-package-evidence-rows").bounding_box()
        report_package_rows_box = page.locator("#sandbox-review-package-report-rows").bounding_box()
        assert review_package_rows_box and evidence_package_rows_box and report_package_rows_box
        assert abs(evidence_package_rows_box["height"] - review_package_rows_box["height"]) <= 4
        assert abs(evidence_package_rows_box["height"] - report_package_rows_box["height"]) <= 4
        assert abs(
            (evidence_package_rows_box["y"] + evidence_package_rows_box["height"])
            - (report_package_rows_box["y"] + report_package_rows_box["height"])
        ) <= 4
        evidence_package_row_heights = page.locator(
            "#sandbox-review-package-evidence-rows .sandbox-review-package-item"
        ).evaluate_all("nodes => nodes.map((node) => node.getBoundingClientRect().height)")
        assert min(evidence_package_row_heights) >= 120
        assert page.locator("#sandbox-review-package-evidence-rows").evaluate(
            "element => element.scrollHeight <= element.clientHeight + 1"
        ) is True
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True
        assert page.evaluate("() => document.scrollingElement.scrollWidth <= window.innerWidth") is True
    finally:
        page.close()


def test_fault_sandbox_replay_report_workbench_tracks_blueprint37(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )
        page.goto(
            f"{demo_server}/fault-injection-sandbox?review=SR-06&trace=ET-04&report=RP-06",
            wait_until="networkidle",
        )

        report_strip = page.locator("#sandbox-report-strip")
        expect(report_strip).to_be_visible()
        expect(report_strip).to_have_attribute("data-blueprint37-surface", "replay-report-workbench")
        expect(report_strip).to_have_attribute(
            "data-blueprint37-contract",
            "controls-timeline-report-preview-candidate-footer",
        )
        expect(page.locator("#fault-sandbox-replay-workbench")).to_be_visible()
        expect(page.locator("#fault-sandbox-replay-controls [data-replay-control]")).to_have_count(4)
        for control_label in ["暂停", "停止", "单步", "重置"]:
            expect(page.locator("#fault-sandbox-replay-controls")).to_contain_text(control_label)
        expect(page.locator("#fault-sandbox-replay-clock")).to_have_text(re.compile(r"00:03:24\s*/\s*00:20:00"))

        timeline = page.locator("#fault-sandbox-replay-timeline")
        expect(timeline).to_be_visible()
        expect(timeline).to_have_attribute("data-blueprint37-contract", "time-markers-sr-et-rp-linkage")
        expect(timeline.locator("[data-replay-marker]")).to_have_count(10)
        expect(timeline.locator("[data-replay-report-id='RP-06']")).to_have_attribute("aria-current", "true")
        expect(page.locator("#fault-sandbox-replay-metrics")).to_contain_text("节点 20/20")
        expect(page.locator("#fault-sandbox-replay-metrics")).to_contain_text("连线 23/23")
        expect(page.locator("#fault-sandbox-replay-metrics")).to_contain_text("冲突 0")
        expect(page.locator("#fault-sandbox-replay-metrics")).to_contain_text("待确认 0")

        report_preview = page.locator("#fault-sandbox-report-preview")
        expect(report_preview).to_have_attribute("data-blueprint37-panel", "report-preview-rail")
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint37-report-row='preview-rail-section']")).to_have_count(7)

        timeline.locator("[data-replay-report-id='RP-07']").click()
        package_summary = page.locator("#fault-sandbox-review-package-summary")
        expect(package_summary).to_have_attribute("data-active-review-row", "SR-07")
        expect(package_summary).to_have_attribute("data-active-trace-id", "ET-03")
        expect(package_summary).to_have_attribute("data-active-report-id", "RP-07")
        expect(timeline.locator("[data-replay-report-id='RP-07']")).to_have_attribute("aria-current", "true")

        for boundary in [
            "sandbox_candidate",
            "truth_effect:none",
            "certification_claim:none",
            "controller_truth_modified:false",
        ]:
            expect(report_strip.locator(f'[data-boundary-token="{boundary}"]')).to_have_count(1)

        assert report_strip.evaluate("(element) => element.getBoundingClientRect().height <= 132") is True
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True
        assert page.evaluate("() => document.scrollingElement.scrollWidth <= window.innerWidth") is True
    finally:
        page.close()


def test_fault_sandbox_replay_timeline_fits_bottom_strip_at_1280(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 820})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )
        page.goto(
            f"{demo_server}/fault-injection-sandbox?review=SR-06&trace=ET-04&report=RP-06",
            wait_until="networkidle",
        )

        report_strip = page.locator("#sandbox-report-strip")
        timeline = page.locator("#fault-sandbox-replay-timeline")
        report_preview = page.locator("#fault-sandbox-report-preview")
        report_section_rows = page.locator("#fault-sandbox-report-section-rows")
        report_actions = page.locator("#sandbox-report-strip .sandbox-report-actions")
        report_invariants = page.locator("#sandbox-report-strip .sandbox-report-invariants")
        expect(report_strip).to_be_visible()
        expect(timeline).to_be_visible()
        expect(report_preview).to_be_visible()
        expect(report_section_rows).to_be_visible()
        expect(report_actions).to_be_visible()
        expect(report_invariants).to_be_visible()
        next_action = page.locator("#fault-sandbox-decision-next-action")
        expect(next_action).to_contain_text("确认后生成修订单")
        assert next_action.evaluate("element => element.scrollWidth <= element.clientWidth + 1") is True
        review_description_boxes = page.locator(
            "#fault-sandbox-review-rows .sandbox-review-row-description-text"
        ).evaluate_all(
            """nodes => nodes.map((node) => ({
              scrollWidth: node.scrollWidth,
              clientWidth: node.clientWidth,
              scrollHeight: node.scrollHeight,
              clientHeight: node.clientHeight,
            }))"""
        )
        assert len(review_description_boxes) == 7
        assert all(box["scrollWidth"] <= box["clientWidth"] + 1 for box in review_description_boxes)
        assert all(box["scrollHeight"] <= box["clientHeight"] + 1 for box in review_description_boxes)
        expect(timeline.locator("[data-replay-marker]")).to_have_count(10)
        report_box = report_strip.bounding_box()
        timeline_box = timeline.bounding_box()
        preview_box = report_preview.bounding_box()
        section_rows_box = report_section_rows.bounding_box()
        actions_box = report_actions.bounding_box()
        invariants_box = report_invariants.bounding_box()
        assert report_box is not None
        assert timeline_box is not None
        assert preview_box is not None
        assert section_rows_box is not None
        assert actions_box is not None
        assert invariants_box is not None
        assert report_box["height"] <= 132
        assert timeline_box["height"] <= 58
        assert actions_box["x"] >= preview_box["x"] + preview_box["width"] + 6
        assert report_actions.evaluate("el => el.scrollHeight <= el.clientHeight + 1")
        action_button_boxes = report_actions.locator("button").evaluate_all(
            """nodes => nodes.map((node) => {
              const rect = node.getBoundingClientRect();
              return {
                bottom: rect.y + rect.height,
                scrollWidth: node.scrollWidth,
                clientWidth: node.clientWidth,
                scrollHeight: node.scrollHeight,
                clientHeight: node.clientHeight,
              };
            })"""
        )
        assert len(action_button_boxes) == 4
        assert all(box["bottom"] <= invariants_box["y"] - 1 for box in action_button_boxes)
        assert all(box["scrollWidth"] <= box["clientWidth"] + 1 for box in action_button_boxes)
        assert all(box["scrollHeight"] <= box["clientHeight"] + 1 for box in action_button_boxes)
        assert report_section_rows.evaluate("el => el.scrollHeight <= el.clientHeight + 1")
        assert timeline.evaluate("el => el.scrollWidth <= el.clientWidth + 1")
        assert timeline.evaluate("el => el.scrollHeight <= el.clientHeight + 1")
        expect(report_preview.locator('[data-blueprint-col="evidence"]:visible')).to_have_count(7)
        report_row_boxes = report_preview.locator(".sandbox-report-section-row").evaluate_all(
            """nodes => nodes.map((node) => {
              const rect = node.getBoundingClientRect();
              const title = node.querySelector(".sandbox-report-section-title");
              const links = node.querySelector(".sandbox-report-section-links");
              return {
                width: rect.width,
                height: rect.height,
                bottom: rect.y + rect.height,
                scrollWidth: node.scrollWidth,
                clientWidth: node.clientWidth,
                titleWidth: title ? title.getBoundingClientRect().width : 0,
                titleScrollWidth: title ? title.scrollWidth : 0,
                titleClientWidth: title ? title.clientWidth : 0,
                linksScrollWidth: links ? links.scrollWidth : 0,
                linksClientWidth: links ? links.clientWidth : 0,
              };
            })"""
        )
        assert report_row_boxes
        assert len(report_row_boxes) == 7
        assert all(box["bottom"] <= section_rows_box["y"] + section_rows_box["height"] + 1 for box in report_row_boxes)
        assert all(box["bottom"] <= invariants_box["y"] - 1 for box in report_row_boxes)
        assert all(box["scrollWidth"] <= box["clientWidth"] + 1 for box in report_row_boxes)
        assert min(box["height"] for box in report_row_boxes) >= 14
        assert min(box["titleWidth"] for box in report_row_boxes) >= 72
        assert all(box["titleScrollWidth"] <= box["titleClientWidth"] + 1 for box in report_row_boxes)
        assert all(box["linksScrollWidth"] <= box["linksClientWidth"] + 1 for box in report_row_boxes)
        marker_label_boxes = timeline.locator("[data-replay-marker] strong").evaluate_all(
            """nodes => nodes.map((node) => ({
              text: node.textContent,
              scrollWidth: node.scrollWidth,
              clientWidth: node.clientWidth,
              scrollHeight: node.scrollHeight,
              clientHeight: node.clientHeight,
            }))"""
        )
        assert marker_label_boxes
        assert all(box["scrollWidth"] <= box["clientWidth"] + 1 for box in marker_label_boxes)
        assert all(box["scrollHeight"] <= box["clientHeight"] + 1 for box in marker_label_boxes)
        action_button_boxes = report_actions.locator("button").evaluate_all(
            """nodes => nodes.map((node) => ({
              scrollWidth: node.scrollWidth,
              clientWidth: node.clientWidth,
            }))"""
        )
        assert action_button_boxes
        assert all(box["scrollWidth"] <= box["clientWidth"] + 1 for box in action_button_boxes)
        marker_boxes = timeline.locator("[data-replay-marker]").evaluate_all(
            """nodes => nodes.map((node) => {
              const rect = node.getBoundingClientRect();
              return {x: rect.x, y: rect.y, width: rect.width, height: rect.height};
            })"""
        )
        assert marker_boxes
        assert min(box["x"] for box in marker_boxes) >= timeline_box["x"] - 1
        assert max(box["x"] + box["width"] for box in marker_boxes) <= (
            timeline_box["x"] + timeline_box["width"] + 1
        )
    finally:
        page.close()


def test_fault_sandbox_default_main_area_uses_replay_canvas_and_report_rail(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )
        page.goto(
            f"{demo_server}/fault-injection-sandbox?review=SR-06&trace=ET-04&report=RP-06",
            wait_until="networkidle",
        )

        shell = page.locator(".sandbox-shell")
        expect(shell).to_have_attribute("data-blueprint37-top-density", "compressed-progress-gates")
        topbar_box = page.locator(".sandbox-topbar").bounding_box()
        process = page.locator("#fault-sandbox-process")
        expect(process).to_be_hidden()
        decision_box = page.locator("#fault-sandbox-decision-board").bounding_box()
        gates_box = page.locator(".sandbox-review-gate-panel").bounding_box()
        assert topbar_box and decision_box and gates_box
        assert topbar_box["height"] <= 60
        assert decision_box["height"] <= 42
        assert gates_box["height"] <= 44

        primary_surface = page.locator("#failure-path")
        primary_box = primary_surface.bounding_box()
        assert primary_box
        assert primary_box["y"] <= 132
        expect(primary_surface).to_have_attribute(
            "data-blueprint37-layout",
            "replay-canvas-report-rail-default",
        )
        replay_panel = page.locator("#fault-sandbox-review-row-panel")
        expect(replay_panel).to_be_visible()
        replay_panel_box = replay_panel.bounding_box()
        assert replay_panel_box
        assert replay_panel_box["y"] <= 226
        expect(replay_panel).to_have_attribute("data-blueprint37-surface", "replay-main-canvas")
        expect(replay_panel).to_have_attribute("data-default-role", "replay-canvas-primary")

        replay_canvas = page.locator("#fault-sandbox-replay-canvas-main")
        expect(replay_canvas).to_be_visible()
        replay_canvas_box = replay_canvas.bounding_box()
        assert replay_canvas_box
        assert replay_canvas_box["y"] <= 270
        expect(replay_canvas).to_have_attribute(
            "data-blueprint37-contract",
            "state-nodes-verified-path-warning-boundary",
        )
        expect(page.locator("#fault-sandbox-replay-canvas-nodes [data-replay-canvas-node]")).to_have_count(12)
        expect(page.locator("#fault-sandbox-replay-canvas-links [data-replay-canvas-link]")).to_have_count(11)
        expect(page.locator("#fault-sandbox-replay-canvas-links [data-replay-link-index]")).to_have_count(11)
        expect(page.locator("#fault-sandbox-replay-canvas-links .sandbox-replay-canvas-link-badge")).to_have_count(11)
        expect(page.locator("#fault-sandbox-replay-canvas-links [data-replay-canvas-link='latch-l1']")).to_have_attribute("aria-current", "true")
        expect(page.locator("#fault-sandbox-replay-canvas-links [data-replay-canvas-link='latch-l2']")).to_have_attribute("aria-current", "true")
        replay_node_overlaps = page.locator("#fault-sandbox-replay-canvas-nodes [data-replay-canvas-node]").evaluate_all(
            """nodes => {
              const boxes = nodes.map((node) => {
                const rect = node.getBoundingClientRect();
                return {
                  id: node.getAttribute("data-replay-canvas-node"),
                  left: rect.left,
                  right: rect.right,
                  top: rect.top,
                  bottom: rect.bottom,
                  scrollHeight: node.scrollHeight,
                  clientHeight: node.clientHeight,
                  scrollWidth: node.scrollWidth,
                  clientWidth: node.clientWidth,
                };
              });
              const overlaps = [];
              for (let i = 0; i < boxes.length; i += 1) {
                for (let j = i + 1; j < boxes.length; j += 1) {
                  const x = Math.min(boxes[i].right, boxes[j].right) - Math.max(boxes[i].left, boxes[j].left);
                  const y = Math.min(boxes[i].bottom, boxes[j].bottom) - Math.max(boxes[i].top, boxes[j].top);
                  if (x > 0.5 && y > 0.5) overlaps.push(`${boxes[i].id}->${boxes[j].id}`);
                }
              }
              return {
                overlaps,
                clipped: boxes
                  .filter((box) => box.scrollHeight > box.clientHeight + 1 || box.scrollWidth > box.clientWidth + 1)
                  .map((box) => box.id),
              };
            }"""
        )
        assert replay_node_overlaps["overlaps"] == []
        assert replay_node_overlaps["clipped"] == []
        _assert_sandbox_replay_blueprint_geometry(page)
        expect(page.locator("#fault-sandbox-replay-canvas-nodes")).to_contain_text("RA")
        expect(page.locator("#fault-sandbox-replay-canvas-nodes")).to_contain_text("L1 告警")
        expect(page.locator("#fault-sandbox-replay-canvas-nodes")).to_contain_text("取消逻辑")
        expect(page.locator("#fault-sandbox-replay-canvas-metrics")).to_contain_text("节点 20/20")
        expect(page.locator("#fault-sandbox-replay-canvas-metrics")).to_contain_text("连线 23/23")

        report_rail = page.locator("#fault-sandbox-main-report-rail")
        inspector = page.locator("#fault-sandbox-diagnosis-inspector")
        package_summary = page.locator("#fault-sandbox-review-package-summary")
        diagnosis_path = inspector.locator(".sandbox-diagnosis-path")
        diagnosis_chain = page.locator("#fault-sandbox-diagnosis-chain")
        evidence_trace = page.locator("#fault-sandbox-evidence-trace")
        diagnosis_summary = page.locator("#fault-sandbox-diagnosis-summary")
        expect(report_rail).to_be_visible()
        expect(page.locator("#fault-sandbox-diagnosis-title")).to_have_text("审查结果")
        expect(inspector).to_have_attribute("data-blueprint37-right-density", "layered-report-evidence")
        expect(inspector).to_have_attribute("data-blueprint37-report-mode", "replay-report-final")
        expect(report_rail).to_have_attribute("data-blueprint37-panel", "right-report-rail")
        expect(report_rail).to_have_attribute("data-blueprint37-right-section", "report-preview")
        expect(report_rail).to_have_attribute("data-blueprint39-default", "status-only")
        expect(package_summary).to_have_attribute("data-blueprint37-right-section", "active-package")
        expect(package_summary).to_be_visible()
        expect(package_summary).to_have_attribute("data-package-state", "active")
        expect(diagnosis_path).to_have_attribute("data-blueprint37-right-section", "diagnosis-summary")
        expect(diagnosis_chain).to_have_attribute("data-blueprint37-right-section", "failure-path")
        expect(evidence_trace).to_have_attribute("data-blueprint37-right-section", "evidence-trace")
        expect(report_rail.locator("[data-main-report-id]")).to_have_count(7)
        expect(report_rail.locator(".sandbox-main-report-row:visible")).to_have_count(1)
        expect(report_rail.locator("[data-report-chapter-kind]")).to_have_count(7)
        expect(report_rail.locator("[data-report-chapter-state='pass']")).to_have_count(5)
        expect(report_rail.locator("[data-report-chapter-state='review']")).to_have_count(1)
        expect(report_rail.locator("[data-report-chapter-state='wait']")).to_have_count(1)
        expect(report_rail.locator(".sandbox-main-report-status")).to_have_count(7)
        expect(report_rail.locator("[data-main-report-id='RP-06']")).to_have_attribute("aria-current", "true")
        expect(report_rail.locator("[data-main-report-id='RP-06']")).to_have_attribute("data-link-state", "active")

        page.locator("#fault-sandbox-report-section-rows [data-report-section-id='RP-07']").click()
        package_summary = page.locator("#fault-sandbox-review-package-summary")
        expect(package_summary).to_have_attribute("data-active-review-row", "SR-07")
        expect(package_summary).to_have_attribute("data-active-trace-id", "ET-03")
        expect(package_summary).to_have_attribute("data-active-report-id", "RP-07")
        expect(report_rail.locator(".sandbox-main-report-row:visible")).to_have_count(1)
        expect(report_rail.locator("[data-main-report-id='RP-07']")).to_have_attribute("aria-current", "true")
        expect(report_rail.locator("[data-main-report-id='RP-07']")).to_have_attribute("data-link-state", "active")
        expect(page.locator("#fault-sandbox-replay-timeline [data-replay-report-id='RP-07']")).to_have_attribute("data-link-state", "active")

        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row")).to_have_count(7)
        canvas_box = replay_canvas.bounding_box()
        inspector_box = inspector.bounding_box()
        evidence_trace_box = evidence_trace.bounding_box()
        rail_box = report_rail.bounding_box()
        report_rows_box = page.locator("#fault-sandbox-main-report-rows").bounding_box()
        diagnosis_summary_box = diagnosis_summary.bounding_box()
        visible_report_row = report_rail.locator(".sandbox-main-report-row:visible").first
        first_report_title = visible_report_row.locator("strong")
        first_report_row_box = visible_report_row.bounding_box()
        package_box = package_summary.bounding_box()
        path_box = diagnosis_path.bounding_box()
        chain_box = diagnosis_chain.bounding_box()
        evidence_rows_box = page.locator("#fault-sandbox-evidence-trace-rows").bounding_box()
        assert canvas_box and inspector_box and evidence_trace_box and rail_box and report_rows_box and diagnosis_summary_box and first_report_row_box and package_box and path_box and chain_box and evidence_rows_box
        assert canvas_box["height"] >= 140
        assert canvas_box["width"] >= 860
        assert rail_box["x"] > canvas_box["x"] + canvas_box["width"] - 8
        assert 250 <= rail_box["width"] <= 360
        assert package_box["y"] < rail_box["y"] < path_box["y"] < chain_box["y"]
        assert path_box["y"] + path_box["height"] <= chain_box["y"] - 2
        assert diagnosis_summary_box["height"] >= 26
        assert diagnosis_summary.evaluate("(element) => element.scrollHeight <= element.clientHeight + 1") is True
        assert diagnosis_path.evaluate("(element) => element.scrollHeight <= element.clientHeight + 1") is True
        diagnosis_path_cards = page.locator(".sandbox-diagnosis-path[data-blueprint37-right-section='diagnosis-summary'] > div").evaluate_all(
            """nodes => nodes.map((node) => {
              const rect = node.getBoundingClientRect();
              return {
                width: rect.width,
                bottom: rect.y + rect.height,
                scrollWidth: node.scrollWidth,
                clientWidth: node.clientWidth,
                scrollHeight: node.scrollHeight,
                clientHeight: node.clientHeight,
              };
            })"""
        )
        assert len(diagnosis_path_cards) == 3
        assert min(card["width"] for card in diagnosis_path_cards) >= 280
        assert all(card["scrollWidth"] <= card["clientWidth"] + 1 for card in diagnosis_path_cards)
        assert all(card["scrollHeight"] <= card["clientHeight"] + 1 for card in diagnosis_path_cards)
        assert max(card["bottom"] for card in diagnosis_path_cards) <= path_box["y"] + path_box["height"] + 1
        diagnosis_chain_cards = diagnosis_chain.locator(".sandbox-diagnosis-chain-node").evaluate_all(
            """nodes => nodes.map((node) => {
              const rect = node.getBoundingClientRect();
              const title = node.querySelector(".sandbox-diagnosis-chain-title");
              const links = node.querySelector(".sandbox-diagnosis-chain-links");
              const stage = node.querySelector(".sandbox-diagnosis-chain-stage");
              const action = node.querySelector(".sandbox-diagnosis-chain-action");
              const titleRect = title ? title.getBoundingClientRect() : null;
              const linksRect = links ? links.getBoundingClientRect() : null;
              const stageRect = stage ? stage.getBoundingClientRect() : null;
              const actionRect = action ? action.getBoundingClientRect() : null;
              return {
                width: rect.width,
                scrollWidth: node.scrollWidth,
                clientWidth: node.clientWidth,
                titleScrollWidth: title ? title.scrollWidth : 0,
                titleClientWidth: title ? title.clientWidth : 0,
                linksScrollWidth: links ? links.scrollWidth : 0,
                linksClientWidth: links ? links.clientWidth : 0,
                titleTop: titleRect ? titleRect.top : 0,
                titleBottom: titleRect ? titleRect.bottom : 0,
                linksTop: linksRect ? linksRect.top : 0,
                chipBottom: Math.max(
                  stageRect ? stageRect.bottom : 0,
                  actionRect ? actionRect.bottom : 0,
                ),
              };
            })"""
        )
        assert len(diagnosis_chain_cards) == 3
        assert min(card["width"] for card in diagnosis_chain_cards) >= 142
        assert all(card["scrollWidth"] <= card["clientWidth"] + 1 for card in diagnosis_chain_cards)
        assert all(card["titleScrollWidth"] <= card["titleClientWidth"] + 1 for card in diagnosis_chain_cards)
        assert all(card["linksScrollWidth"] <= card["linksClientWidth"] + 1 for card in diagnosis_chain_cards)
        assert all(card["chipBottom"] <= card["titleTop"] + 0.5 for card in diagnosis_chain_cards)
        assert all(card["titleBottom"] <= card["linksTop"] + 0.5 for card in diagnosis_chain_cards)
        assert 66 <= chain_box["height"] <= 80
        assert 26 <= report_rows_box["height"] <= 44
        assert first_report_row_box["height"] >= 26
        assert first_report_title.evaluate("(element) => element.scrollWidth <= element.clientWidth + 1") is True
        assert report_rail.evaluate("(element) => element.scrollHeight <= element.clientHeight + 1") is True
        assert report_rows_box["height"] < package_box["height"]
        assert evidence_trace.evaluate("(element) => element.closest('#fault-sandbox-diagnosis-inspector') !== null") is True
        expect(evidence_trace.locator(".sandbox-evidence-trace-row:visible")).to_have_count(1)
        assert evidence_trace_box["x"] >= inspector_box["x"] - 1
        assert evidence_trace_box["x"] + evidence_trace_box["width"] <= inspector_box["x"] + inspector_box["width"] + 1
        assert evidence_trace_box["y"] >= chain_box["y"] + chain_box["height"]
        assert evidence_trace_box["height"] <= 94
        assert 26 <= evidence_rows_box["height"] <= 56
        assert inspector.evaluate("(element) => element.scrollHeight <= element.clientHeight + 1") is True
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True
        assert page.evaluate("() => document.scrollingElement.scrollWidth <= window.innerWidth") is True
    finally:
        page.close()


def test_fault_sandbox_blueprint37_canvas_and_report_actions_share_visual_system(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )
        page.goto(
            f"{demo_server}/fault-injection-sandbox?review=SR-06&trace=ET-04&report=RP-06",
            wait_until="networkidle",
        )

        replay_canvas = page.locator("#fault-sandbox-replay-canvas-main")
        report_strip = page.locator("#sandbox-report-strip")
        report_rail = page.locator("#fault-sandbox-main-report-rail")
        expect(replay_canvas).to_have_attribute("data-blueprint37-density", "wide-replay-canvas")
        expect(report_strip).to_have_attribute("data-blueprint37-system", "replay-report-shared")
        expect(report_rail).to_have_attribute("data-blueprint37-system", "replay-report-shared")
        expect(page.locator("#fault-sandbox-main-report-actions [data-main-report-action]")).to_have_count(2)
        expect(page.locator("#fault-sandbox-main-report-actions [data-main-report-action='revision']")).to_have_text("生成报告")
        expect(page.locator("#fault-sandbox-main-report-actions [data-main-report-action='export']")).to_have_text("导出全部")
        expect(page.locator("#fault-sandbox-main-report-actions [data-main-report-action='export']")).to_have_attribute("data-report-primary-action", "review-package")

        canvas_box = replay_canvas.bounding_box()
        assert canvas_box
        assert canvas_box["height"] >= 140
        assert canvas_box["width"] >= 600
        assert canvas_box["width"] / canvas_box["height"] >= 3.0

        page.locator("#fault-sandbox-main-report-actions [data-main-report-action='export']").click()
        expect(page.locator("#sandbox-review-package-panel")).to_be_visible()
        expect(page.locator('#sandbox-review-package-invariants [data-boundary-token="truth_effect:none"]')).to_have_count(1)
        page.locator("#sandbox-review-package-close").click()
        expect(page.locator("#sandbox-review-package-panel")).to_be_hidden()
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True
        assert page.evaluate("() => document.scrollingElement.scrollWidth <= window.innerWidth") is True
    finally:
        page.close()


def test_fault_prepare_and_sandbox_rows_share_density_scan_contract(
  demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirementsPayload, drawingPayload, faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirementsPayload));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawingPayload));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION, _dense_sandbox_plan()],
        )

        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="networkidle")
        matrix_rows = page.locator("#fault-candidate-matrix-body [data-row-scan-kind='fault-matrix']")
        expect(matrix_rows).to_have_count(1)
        matrix_row = matrix_rows.first
        expect(matrix_row).to_have_attribute("data-row-scan-contract", "id-status-evidence-link")
        for token in ["id", "status", "evidence", "link"]:
            expect(matrix_row.locator(f"[data-row-scan-token='{token}']")).to_be_visible()
        expect(matrix_row.locator("[data-row-scan-token='evidence']")).to_have_text("SRC-01")
        assert matrix_row.bounding_box()["height"] <= 60
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True

        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="networkidle")
        review_row = page.locator("[data-blueprint-review-row='SR-06']")
        expect(page.locator("#fault-sandbox-review-rows [data-row-scan-kind='sandbox-review']")).to_have_count(7)
        expect(review_row).to_have_attribute("data-row-scan-contract", "id-status-evidence-link")
        for token in ["id", "status", "evidence", "link"]:
            expect(review_row.locator(f"[data-row-scan-token='{token}']")).to_be_visible()

        report_row = page.locator("[data-report-section-id='RP-06']")
        expect(page.locator("#fault-sandbox-report-section-rows [data-row-scan-kind='replay-report']")).to_have_count(7)
        expect(report_row).to_have_attribute("data-row-scan-contract", "id-status-evidence-link")
        for token in ["id", "status", "evidence", "link"]:
            expect(report_row.locator(f"[data-row-scan-token='{token}']")).to_be_visible()
        expect(report_row.locator("[data-row-scan-token='link'] [data-link-kind='trace']")).to_have_text("ET-04")
        assert report_row.bounding_box()["height"] <= 28
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True
        assert page.evaluate("() => document.scrollingElement.scrollWidth <= window.innerWidth") is True
    finally:
        page.close()


def test_fault_matrix_selection_carries_review_linkage_into_sandbox(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        fault_payload = {
            **FAULT_PREPARATION,
            "injection_points": [
                {
                    **FAULT_PREPARATION["injection_points"][0],
                    "constraint_zh": "truth_effect:none；controller_truth_modified:false。",
                }
            ],
        }
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirementsPayload, drawingPayload, faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirementsPayload));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawingPayload));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), fault_payload, _dense_sandbox_plan()],
        )

        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="networkidle")
        matrix_row = page.locator("#fault-candidate-matrix-body [data-row-scan-kind='fault-matrix']").first
        matrix_row.click()

        expect(matrix_row).to_have_class(re.compile("is-linked-active"))
        expect(matrix_row).to_have_attribute("data-linked-review-row", "SR-06")
        expect(matrix_row).to_have_attribute("data-linked-trace-id", "ET-04")
        expect(matrix_row).to_have_attribute("data-linked-report-id", "RP-06")
        summary = page.locator("#fault-context-link-summary")
        expect(summary).to_be_visible()
        expect(summary).to_have_attribute("data-active-review-row", "SR-06")
        expect(summary).to_have_attribute("data-active-trace-id", "ET-04")
        expect(summary).to_have_attribute("data-active-report-id", "RP-06")
        for token in ["沙盒预选", "SR-06", "ET-04", "RP-06"]:
            expect(summary).to_contain_text(token)
        for boundary in ["sandbox_candidate", "truth_effect:none", "controller_truth_modified:false"]:
            expect(summary.locator(f'[data-boundary-token="{boundary}"]')).to_have_count(1)
        context_details = page.locator("#fault-context-body dl")
        for boundary in ["truth_effect:none", "controller_truth_modified:false"]:
            expect(context_details.locator(f'[data-boundary-token="{boundary}"]')).to_have_count(1)
            assert boundary not in context_details.inner_text()

        page.locator("#fault-context-close").click()
        for index in range(page.locator("textarea[data-boundary-id]").count()):
            page.locator("textarea[data-boundary-id]").nth(index).fill("确认空跑演示边界。")
        expect(page.locator("#fault-sandbox-next")).to_be_enabled()
        page.locator("#fault-sandbox-next").click()
        page.wait_for_url(re.compile(r".*/fault-injection-sandbox\?review=SR-06&trace=ET-04&report=RP-06$"))

        review_row = page.locator("[data-blueprint-review-row='SR-06']")
        expect(review_row).to_have_attribute("aria-selected", "true")
        expect(review_row).to_have_class(re.compile("is-active"))
        expect(page.locator("#fault-sandbox-diagnosis-inspector")).to_have_attribute("data-active-review-row", "SR-06")
        expect(page.locator("#fault-sandbox-affected-path")).to_have_attribute("data-linked-trace-id", "ET-04")
        expect(page.locator("[data-evidence-trace-id='ET-04']")).to_have_class(re.compile("is-linked-active"))
        expect(page.locator("[data-report-section-id='RP-06']")).to_have_class(re.compile("is-linked-active"))
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True
        assert page.evaluate("() => document.scrollingElement.scrollWidth <= window.innerWidth") is True
    finally:
        page.close()


def test_fault_sandbox_active_review_package_summary_is_default_readable(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    model_calls: list[str] = []
    tick_calls: list[str] = []
    try:
        def reject_model_call(route: Any) -> None:
            model_calls.append(route.request.url)
            route.fulfill(status=500, content_type="application/json", body='{"error":"model_call_forbidden"}')

        page.route("**/api/requirements-intake/prepare-fault-injection/sandbox", reject_model_call)
        page.route("**/api/tick", lambda route: (tick_calls.append(route.request.url), route.abort()))
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )

        page.goto(
            f"{demo_server}/fault-injection-sandbox?review=SR-06&trace=ET-04&report=RP-06",
            wait_until="networkidle",
        )
        package_summary = page.locator("#fault-sandbox-review-package-summary")
        expect(package_summary).to_be_visible()
        expect(package_summary).to_have_attribute("data-blueprint-surface", "active-review-package-summary")
        expect(package_summary).to_have_attribute("data-package-state", "active")
        expect(package_summary).to_have_attribute("data-active-review-row", "SR-06")
        expect(package_summary).to_have_attribute("data-active-trace-id", "ET-04")
        expect(package_summary).to_have_attribute("data-active-report-id", "RP-06")
        expect(package_summary.locator("[data-package-summary-token='review']")).to_have_text("SR-06")
        expect(package_summary.locator("[data-package-summary-token='trace']")).to_have_text("ET-04")
        expect(package_summary.locator("[data-package-summary-token='report']")).to_have_text("RP-06")
        for token in ["报告可追溯", "沙盒审查", "未决问题", "建议修复", "关键证据"]:
            expect(package_summary).to_contain_text(token)
        for boundary in ["truth_effect:none", "controller_truth_modified:false"]:
            expect(package_summary.locator(f'[data-boundary-token="{boundary}"]')).to_have_count(1)
        expect(page.locator("#sandbox-review-package-panel")).to_be_hidden()
        package_summary_height = package_summary.bounding_box()["height"]
        assert 46 <= package_summary_height <= 54
        assert package_summary.evaluate(
            """(element) => {
              const summary = element.getBoundingClientRect();
              const inspector = document.querySelector("#fault-sandbox-diagnosis-inspector").getBoundingClientRect();
              return summary.bottom <= inspector.bottom;
            }"""
        ) is True
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True

        page.locator('[data-blueprint-review-row="SR-07"]').click()
        expect(package_summary).to_have_attribute("data-active-review-row", "SR-07")
        expect(package_summary).to_have_attribute("data-active-trace-id", "ET-03")
        expect(package_summary).to_have_attribute("data-active-report-id", "RP-07")
        expect(package_summary).to_contain_text("未决风险")
        expect(package_summary).to_contain_text("控制真相未修改")

        page.locator("#sandbox-evidence-close").click()
        page.locator('[data-report-section-id="RP-06"]').click()
        expect(package_summary).to_have_attribute("data-active-review-row", "SR-06")
        expect(package_summary).to_have_attribute("data-active-trace-id", "ET-04")
        expect(package_summary).to_have_attribute("data-active-report-id", "RP-06")
        expect(page.locator('[data-blueprint-review-row="SR-06"]')).to_have_attribute("aria-selected", "true")
        assert page.evaluate("() => document.scrollingElement.scrollWidth <= window.innerWidth") is True
        assert model_calls == []
        assert tick_calls == []
    finally:
        page.close()


def test_desktop_logic_builder_draws_cockpit_control_console_and_main_display(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="domcontentloaded")
        _show_logic_builder_workbench(page)
        cockpit = page.locator('[data-ui-skin="codex-minimal"]')
        console = page.locator('[data-cockpit-role="control-console"]')
        display = page.locator('[data-cockpit-role="primary-display"]')
        expect(cockpit).to_be_visible()
        expect(cockpit).to_have_attribute("data-left-rail-state", "collapsed")
        expect(page.locator('[data-cockpit-role="canopy-frame"]')).to_be_hidden()
        expect(page.locator('[data-cockpit-role="status-banner"]')).to_be_visible()
        expect(page.locator('[data-cockpit-role="mission-strip"]')).to_be_visible()
        page.click('#logic-collapsed-tool-rail [data-panel-toggle="left"]')
        expect(cockpit).to_have_attribute("data-left-rail-state", "expanded")
        expect(console).to_be_visible()
        expect(display).to_be_visible()
        expect(page.locator(".logic-cockpit-canopy-window")).to_have_count(3)
        expect(page.locator("#logic-circuit-eval-panel")).to_be_visible()
        assert page.locator("#logic-circuit-input-details").evaluate("element => element.open") is True
        for selector in [
            "#logic-circuit-tra",
            "#logic-circuit-ra",
            "#logic-circuit-n1k",
            "#logic-circuit-vdt",
        ]:
            expect(page.locator(selector)).to_be_visible()

        console_box = console.bounding_box()
        display_box = display.bounding_box()
        canvas_box = page.locator("#logic-canvas").bounding_box()
        assert console_box is not None
        assert display_box is not None
        assert canvas_box is not None
        assert display_box["y"] < console_box["y"]
        assert display_box["width"] >= 850
        assert canvas_box["height"] >= 360
    finally:
        page.close()


def test_logic_builder_unknown_node_kind_uses_readable_fallback(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    drawing = json.loads(json.dumps(LOGIC_DRAWING))
    drawing["nodes"][1]["node_kind"] = "backend_gate_raw"
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            drawing,
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        raw_kind_node = page.locator('.logic-node[data-node-id="gate_release"]')
        expect(raw_kind_node).to_have_attribute("data-kind", "backend_gate_raw")
        expect(raw_kind_node.locator(".logic-node-kind")).to_have_text("逻辑")
        expect(raw_kind_node.locator(".logic-node-kind")).not_to_have_text("backend_gate_raw")
    finally:
        page.close()


def test_fault_sandbox_source_deferred_replay_does_not_claim_config_generated(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    source_scope = {
        "fault_injection": {
            "status": "source_deferred",
            "reason_zh": "源文档声明故障注入本轮暂不考虑。",
        }
    }
    fault_payload = {
        **FAULT_PREPARATION,
        "status": "source_deferred",
        "summary_zh": "源文档声明故障注入本轮暂不考虑。",
        "source_scope": source_scope,
        "fault_scenarios": [],
        "injection_points": [],
        "boundary_questions": [],
        "boundary_answers": [],
    }
    sandbox_payload = {
        **SANDBOX_PLAN,
        "status": "source_deferred",
        "summary_zh": "源文档声明故障注入暂缓，未生成沙盒注入计划。",
        "source_scope": source_scope,
        "sandbox_injection_plan": [],
        "observation_points": [],
        "review_checklist": [],
    }
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [fault_payload, sandbox_payload],
        )
        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="networkidle")
        expect(page.locator("#fault-sandbox-result-state")).to_have_text("源文档暂缓")
        expect(page.locator("#fault-sandbox-result-summary")).to_contain_text("未生成沙盒注入计划")
        expect(page.locator("#fault-sandbox-review-gate")).to_have_text("源文档暂缓")
        expect(page.locator("#fault-sandbox-quality-summary")).to_contain_text("0 个沙盒计划")
        expect(page.locator("#fault-sandbox-revision-next")).to_be_disabled()
        for index in range(page.locator("input[data-sandbox-confirm]").count()):
            expect(page.locator("input[data-sandbox-confirm]").nth(index)).to_be_disabled()
    finally:
        page.close()


def test_fault_routes_first_visit_show_candidate_preview_without_seeded_storage(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    model_calls: list[str] = []
    tick_calls: list[str] = []
    try:
        def reject_model_call(route: Any) -> None:
            model_calls.append(route.request.url)
            route.fulfill(status=500, content_type="application/json", body='{"error":"model_call_forbidden"}')

        page.route("**/api/requirements-intake/prepare-fault-injection", reject_model_call)
        page.route("**/api/requirements-intake/prepare-fault-injection/sandbox", reject_model_call)
        page.route("**/api/tick", lambda route: (tick_calls.append(route.request.url), route.abort()))

        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate("localStorage.clear()")
        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="domcontentloaded")
        expect(page.locator("#fault-result-state")).to_have_text("候选已生成")
        expect(page.locator("#fault-result-summary")).to_contain_text("首次进入已载入本地蓝图候选预览")
        expect(page.locator("#fault-source-title")).to_have_text("蓝图候选预览")
        expect(page.locator("#fault-source-summary")).to_contain_text("不会调用模型")
        expect(page.locator("#fault-injection-workflow-stage")).to_have_text("蓝图候选预览")
        expect(page.locator("#fault-decision-candidate-summary")).to_have_text("2 场景 · 2 注入点")
        expect(page.locator("#fault-boundary-progress")).to_have_text("2/2 已回答")
        expect(page.locator("#fault-sandbox-next")).to_be_enabled()
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint33-row='fault-matrix']")).to_have_count(2)
        assert page.locator("#fault-candidate-matrix-body .fault-matrix-path-token").count() >= 4

        preview_contract = page.evaluate(
            """() => {
              const fault = JSON.parse(localStorage.getItem("ai-fantui-fault-injection-preparation-v1"));
              const sandbox = JSON.parse(localStorage.getItem("ai-fantui-fault-injection-sandbox-plan-v1"));
              return {
                fault: {
                  first_visit_preview: fault.first_visit_preview,
                  candidate_state: fault.candidate_state,
                  truth_effect: fault.truth_effect,
                  certification_claim: fault.certification_claim,
                  controller_truth_modified: fault.controller_truth_modified,
                  model: fault.llm && fault.llm.model,
                },
                sandbox: {
                  first_visit_preview: sandbox.first_visit_preview,
                  candidate_state: sandbox.candidate_state,
                  truth_effect: sandbox.truth_effect,
                  certification_claim: sandbox.certification_claim,
                  controller_truth_modified: sandbox.controller_truth_modified,
                  execution_contract: sandbox.execution_contract,
                },
              };
            }"""
        )
        assert preview_contract == {
            "fault": {
                "first_visit_preview": True,
                "candidate_state": "fault_injection_preparation",
                "truth_effect": "none",
                "certification_claim": "none",
                "controller_truth_modified": False,
                "model": "blueprint-candidate-preview",
            },
            "sandbox": {
                "first_visit_preview": True,
                "candidate_state": "sandbox_candidate",
                "truth_effect": "none",
                "certification_claim": "none",
                "controller_truth_modified": False,
                "execution_contract": {"run_tick": False, "simulate": False, "dry_run_only": True},
            },
        }

        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate("localStorage.clear()")
        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="domcontentloaded")
        expect(page.locator("#fault-sandbox-result-state")).to_have_text("配置已生成")
        expect(page.locator("#fault-sandbox-result-summary")).to_contain_text("首次进入已载入本地蓝图沙盒预览")
        expect(page.locator("#fault-sandbox-source-title")).to_have_text("已载入故障准备草稿")
        expect(page.locator("#fault-sandbox-source-summary")).to_contain_text("首次进入已载入本地蓝图故障候选预览")
        expect(page.locator("#fault-sandbox-plan-count")).to_have_text("2 计划")
        expect(page.locator("#fault-sandbox-observation-count")).to_have_text("2 观测点")
        expect(page.locator("#fault-sandbox-review-count")).to_have_text("2 审查项")
        expect(page.locator("#fault-sandbox-review-row-count")).to_have_text("7 行")
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint36-row='sandbox-review']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-diagnosis-chain [data-blueprint36-chain-node='failure-path']")).to_have_count(3)
        expect(page.locator("#fault-sandbox-evidence-trace-rows [data-blueprint36-evidence-row='evidence-chain']")).to_have_count(4)
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint36-report-row='replay-report']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-plan-coverage-list")).to_contain_text("首次进入蓝图沙盒预览")
        expect(page.locator("#fault-sandbox-plan-coverage-list")).not_to_contain_text("ui_blueprint_first_visit_preview")
        expect(page.locator("#fault-sandbox-review-gate")).to_have_text("需确认 3 个一级闸门")

        sandbox_contract = page.evaluate(
            """() => {
              const fault = JSON.parse(localStorage.getItem("ai-fantui-fault-injection-preparation-v1"));
              const sandbox = JSON.parse(localStorage.getItem("ai-fantui-fault-injection-sandbox-plan-v1"));
              return {
                faultFirstVisit: fault.first_visit_preview,
                sandboxFirstVisit: sandbox.first_visit_preview,
                candidateState: sandbox.candidate_state,
                truthEffect: sandbox.truth_effect,
                certificationClaim: sandbox.certification_claim,
                controllerTruthModified: sandbox.controller_truth_modified,
                executionContract: sandbox.execution_contract,
              };
            }"""
        )
        assert sandbox_contract == {
            "faultFirstVisit": True,
            "sandboxFirstVisit": True,
            "candidateState": "sandbox_candidate",
            "truthEffect": "none",
            "certificationClaim": "none",
            "controllerTruthModified": False,
            "executionContract": {"run_tick": False, "simulate": False, "dry_run_only": True},
        }
        assert model_calls == []
        assert tick_calls == []
    finally:
        page.close()


def test_source_deferred_fault_path_can_load_blueprint_candidate_sandbox_preview(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    model_calls: list[str] = []
    tick_calls: list[str] = []
    source_scope = {
        "fault_injection": {
            "status": "source_deferred",
            "reason_zh": "源文档声明故障注入本轮暂不考虑。",
            "source_anchors": [
                {"id": "B91", "kind": "范围约束", "origin": "docx_body", "quote_zh": "故障注入目前暂时不考虑，很复杂。"}
            ],
        }
    }
    requirements = {**REQUIREMENTS_READY, "source_scope": source_scope}
    fault_payload = {
        **FAULT_PREPARATION,
        "status": "source_deferred",
        "summary_zh": "源文档声明故障注入本轮暂不考虑。",
        "source_scope": source_scope,
        "fault_scenarios": [],
        "injection_points": [],
        "boundary_questions": [],
        "boundary_answers": [],
    }
    sandbox_payload = {
        **SANDBOX_PLAN,
        "status": "source_deferred",
        "summary_zh": "源文档声明故障注入暂缓，未生成沙盒注入计划。",
        "source_scope": source_scope,
        "sandbox_injection_plan": [],
        "observation_points": [],
        "review_checklist": [],
    }
    try:
        def reject_model_call(route: Any) -> None:
            model_calls.append(route.request.url)
            route.fulfill(status=500, content_type="application/json", body='{"error":"model_call_forbidden"}')

        page.route("**/api/requirements-intake/prepare-fault-injection", reject_model_call)
        page.route("**/api/requirements-intake/prepare-fault-injection/sandbox", reject_model_call)
        page.route("**/api/tick", lambda route: (tick_calls.append(route.request.url), route.abort()))
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [requirements, _circuit_view_drawing(), fault_payload, sandbox_payload],
        )

        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="networkidle")
        expect(page.locator("#fault-result-state")).to_have_text("源文档暂缓")
        expect(page.locator("#fault-source-defer")).to_be_visible()
        expect(page.locator("#fault-source-defer-summary")).to_contain_text("源文档声明故障注入本轮暂不考虑")
        expect(page.locator("#fault-blueprint-candidate-actions")).to_be_visible()
        expect(page.locator("#fault-load-blueprint-candidate")).to_be_enabled()
        page.click("#fault-load-blueprint-candidate")
        expect(page.locator("#fault-result-state")).to_have_text("候选已生成")
        expect(page.locator("#fault-result-summary")).to_contain_text("蓝图候选演示已载入")
        expect(page.locator("#fault-blueprint-candidate-status")).to_have_text("已载入沙盒候选，不改变源文档范围")
        expect(page.locator("#fault-decision-candidate-summary")).to_have_text("2 场景 · 2 注入点")
        expect(page.locator("#fault-boundary-progress")).to_have_text("2/2 已回答")
        expect(page.locator("#fault-decision-boundary-summary")).to_have_text("2/2 已回答")
        expect(page.locator("#fault-decision-next-action")).to_contain_text("可进入沙盒")
        expect(page.locator("#fault-decision-next-action")).to_contain_text("证据链和报告预览")
        expect(page.locator("#fault-candidate-matrix-panel")).to_be_visible()
        expect(page.locator("#fault-candidate-matrix-count")).to_have_text("2 行")
        expect(page.locator(".fault-candidate-matrix[data-blueprint-density='compact-workbench']")).to_be_visible()
        expect(page.locator("#fault-candidate-matrix-body [data-fault-matrix-row]")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-fault-row='matrix']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint33-row='fault-matrix']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-density='compact-workbench']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body .blueprint-row--fault-matrix")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body .blueprint-density-row")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-row-pattern='shared-v1']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-col='checkbox']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-col='injection-position']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-col='covered-path']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-col='risk']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-col='state']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body .fault-matrix-select input[disabled]")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body .fault-matrix-pathline")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body .fault-matrix-pathline").first).to_have_attribute(
            "data-blueprint39-detail", "selected-only"
        )
        expect(page.locator("#fault-candidate-matrix-body .fault-matrix-path-summary")).to_have_count(2)
        assert page.locator("#fault-candidate-matrix-body .fault-matrix-path-token").count() >= 4
        assert page.locator("#fault-candidate-matrix-body .blueprint-row-token").count() >= 6
        assert page.locator("#fault-candidate-matrix-body .blueprint-row-chip").count() >= 6
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint33-row='fault-matrix']").first).to_have_attribute(
            "data-blueprint-columns", re.compile("covered-path")
        )
        fault_row_box = page.locator("#fault-candidate-matrix-body [data-blueprint-density='compact-workbench']").first.bounding_box()
        assert fault_row_box
        assert fault_row_box["height"] <= 60
        fault_row_style = page.locator(
            "#fault-candidate-matrix-body [data-blueprint33-row='fault-matrix']"
        ).first.locator("td").nth(1).evaluate(
            """(element) => {
              const style = getComputedStyle(element);
              return {
                backgroundColor: style.backgroundColor,
                backgroundImage: style.backgroundImage,
              };
            }"""
        )
        assert fault_row_style["backgroundColor"] in {"rgb(255, 255, 255)", "rgb(247, 251, 255)"}
        assert "30, 103, 255" in fault_row_style["backgroundImage"]
        id_token_metrics = page.locator("#fault-candidate-matrix-body .fault-matrix-id code").evaluate_all(
            """nodes => nodes.map((node) => ({
              text: node.textContent,
              rawId: node.getAttribute("data-raw-row-id"),
              clientWidth: node.clientWidth,
              scrollWidth: node.scrollWidth,
            }))"""
        )
        assert id_token_metrics
        assert [item["text"] for item in id_token_metrics] == ["F-01", "F-02"]
        assert [item["rawId"] for item in id_token_metrics] == ["blueprint_fault_ra_low", "blueprint_fault_sw_path"]
        assert all(item["scrollWidth"] <= item["clientWidth"] + 1 for item in id_token_metrics), id_token_metrics
        expect(page.locator("#fault-candidate-matrix-panel")).to_contain_text("覆盖路径")
        expect(page.locator("#fault-candidate-matrix-body")).to_contain_text("无线电高度")
        expect(page.locator("#fault-candidate-matrix-body .fault-matrix-injection-cell").first).not_to_contain_text("radio_altitude_ft")
        expect(page.locator("#fault-candidate-matrix-body [data-raw-node-id='radio_altitude_ft']")).to_have_text("RA 高度")
        expect(page.locator("#fault-candidate-matrix-body [data-raw-signal-name='radio_altitude_ft']")).to_have_text("无线电高度")
        expect(page.locator(".fault-scenario-card")).to_have_count(2)
        expect(page.locator(".fault-point-card")).to_have_count(2)
        expect(page.locator("#fault-coverage-evidence-list .fault-coverage-row")).to_have_count(3)
        expect(page.locator("#fault-coverage-evidence-list")).to_contain_text("界面蓝图候选预览")
        expect(page.locator("#fault-coverage-evidence-list")).not_to_contain_text("ui_blueprint_candidate_preview")
        expect(page.locator("#fault-sandbox-next")).to_be_enabled()
        preview_contract = page.evaluate(
            """() => {
              const fault = JSON.parse(localStorage.getItem("ai-fantui-fault-injection-preparation-v1"));
              const sandbox = JSON.parse(localStorage.getItem("ai-fantui-fault-injection-sandbox-plan-v1"));
              return {
                fault: {
                  ui_blueprint_preview: fault.ui_blueprint_preview,
                  candidate_state: fault.candidate_state,
                  truth_effect: fault.truth_effect,
                  certification_claim: fault.certification_claim,
                  controller_truth_modified: fault.controller_truth_modified,
                  model: fault.llm && fault.llm.model,
                },
                sandbox: {
                  ui_blueprint_preview: sandbox.ui_blueprint_preview,
                  candidate_state: sandbox.candidate_state,
                  truth_effect: sandbox.truth_effect,
                  certification_claim: sandbox.certification_claim,
                  controller_truth_modified: sandbox.controller_truth_modified,
                  execution_contract: sandbox.execution_contract,
                  completion_strategy: sandbox.plan_coverage_completion && sandbox.plan_coverage_completion.strategy,
                },
              };
            }"""
        )
        assert preview_contract == {
            "fault": {
                "ui_blueprint_preview": True,
                "candidate_state": "fault_injection_preparation",
                "truth_effect": "none",
                "certification_claim": "none",
                "controller_truth_modified": False,
                "model": "blueprint-candidate-preview",
            },
            "sandbox": {
                "ui_blueprint_preview": True,
                "candidate_state": "sandbox_candidate",
                "truth_effect": "none",
                "certification_claim": "none",
                "controller_truth_modified": False,
                "execution_contract": {"run_tick": False, "simulate": False, "dry_run_only": True},
                "completion_strategy": "ui_blueprint_candidate_preview",
            },
        }

        page.click("#fault-sandbox-next")
        page.wait_for_url("**/fault-injection-sandbox")
        expect(page.locator("#fault-sandbox-result-state")).to_have_text("配置已生成")
        expect(page.locator("#fault-sandbox-result-summary")).to_contain_text("蓝图候选沙盒计划已载入")
        contract = page.locator("#fault-sandbox-contract")
        for token in ["run_tick:false", "simulate:false", "dry_run_only:true"]:
            expect(contract.locator(f'[data-contract-token="{token}"]')).to_have_count(1)
            assert token not in contract.inner_text()
        expect(page.locator("#fault-sandbox-plan-count")).to_have_text("2 计划")
        expect(page.locator("#fault-sandbox-plan-coverage-list")).to_contain_text("界面蓝图候选预览")
        expect(page.locator("#fault-sandbox-plan-coverage-list")).not_to_contain_text("ui_blueprint_candidate_preview")
        expect(page.locator("#fault-sandbox-review-gate")).to_have_text("需确认 3 个一级闸门")
        expect(page.locator(".sandbox-evidence-tile")).to_have_count(4)
        expect(page.locator("#fault-sandbox-review-row-panel")).to_be_visible()
        expect(page.locator("#fault-sandbox-review-row-count")).to_have_text("7 行")
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row-header")).to_be_visible()
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows .blueprint-row--sandbox-review")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint-row-pattern='shared-v1']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint-review-row]")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint36-row='sandbox-review']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint36-row='sandbox-review'] [data-blueprint-col='trace-report']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row-decision")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row-link-token")).to_have_count(14)
        assert page.locator("#fault-sandbox-review-rows .blueprint-row-token").count() >= 21
        expect(page.locator("[data-blueprint-review-row='SR-06'] [data-link-kind='trace']")).to_have_text("ET-04")
        expect(page.locator("[data-blueprint-review-row='SR-06'] [data-link-kind='report']")).to_have_text("RP-06")
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row-check input[disabled]")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows")).to_contain_text("报告可追溯")
        expect(page.locator("#fault-sandbox-diagnosis-inspector")).to_be_visible()
        expect(page.locator("#fault-sandbox-diagnosis-summary")).to_contain_text("空跑")
        expect(page.locator("#fault-sandbox-affected-path")).to_have_text("RA -> RA")
        expect(page.locator("#fault-sandbox-first-abnormal-node")).to_have_text("RA")
        expect(page.locator("#fault-sandbox-diagnosis-chain [data-blueprint36-chain-node='failure-path']")).to_have_count(3)
        expect(page.locator("#fault-sandbox-diagnosis-chain .blueprint-row--diagnosis-chain")).to_have_count(3)
        expect(page.locator("#fault-sandbox-diagnosis-chain [data-blueprint-row-pattern='shared-v1']")).to_have_count(3)
        expect(page.locator("#fault-sandbox-diagnosis-chain .sandbox-diagnosis-chain-link-token")).to_have_count(6)
        expect(page.locator("#fault-sandbox-diagnosis-evidence-links [data-blueprint36-evidence-link='diagnosis']")).to_have_count(3)
        expect(page.locator("#fault-sandbox-evidence-trace-rows .sandbox-evidence-trace-row")).to_have_count(4)
        expect(page.locator("#fault-sandbox-evidence-trace-rows .blueprint-row--evidence-chain")).to_have_count(4)
        expect(page.locator("#fault-sandbox-evidence-trace-rows [data-blueprint36-evidence-row='evidence-chain']")).to_have_count(4)
        expect(page.locator("#fault-sandbox-evidence-trace-rows [data-blueprint-row-pattern='shared-v1']")).to_have_count(4)
        expect(page.locator("#fault-sandbox-evidence-trace-rows .sandbox-evidence-trace-link-token")).to_have_count(8)
        expect(page.locator("[data-evidence-trace-id='ET-04'] [data-link-kind='report']")).to_have_text("RP-06")
        expect(page.locator("#fault-sandbox-evidence-trace-rows")).to_contain_text("报告预览")
        expect(page.locator("#fault-sandbox-report-preview")).to_be_visible()
        expect(page.locator("#fault-sandbox-report-section-rows .sandbox-report-section-row")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows .blueprint-row--replay-report")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint-report-row='review-package-section']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint36-report-row='replay-report']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint-row-pattern='shared-v1']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows .sandbox-report-section-decision")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows .sandbox-report-link-token")).to_have_count(14)
        expect(page.locator("[data-report-section-id='RP-06'] [data-link-kind='trace']")).to_have_text("ET-04")
        expect(page.locator("[data-report-section-id='RP-06'] [data-link-kind='report']")).to_have_text("RP-06")
        expect(page.locator("#fault-sandbox-report-section-rows")).to_contain_text("沙盒审查")
        page.locator("#fault-sandbox-report-section-rows .sandbox-report-section-row").first.click()
        expect(page.locator("#sandbox-evidence-popover")).to_be_visible()
        expect(page.locator("#sandbox-evidence-body")).to_contain_text("报告章节")
        page.locator("#sandbox-evidence-close").click()
        expect(page.locator(".sandbox-review-item")).to_have_count(2)
        expect(page.locator("#fault-sandbox-detail-drawer")).to_be_hidden()
        expect(page.locator("#fault-sandbox-toggle-detail-panel")).to_have_attribute("aria-expanded", "false")
        page.click("#fault-sandbox-toggle-detail-panel")
        expect(page.locator("#fault-sandbox-detail-drawer")).to_be_visible()
        expect(page.locator("#fault-sandbox-toggle-detail-panel")).to_have_attribute("aria-expanded", "true")
        page.locator("#fault-sandbox-review-details > summary").click()
        expect(page.locator(".sandbox-review-item").first).to_be_visible()
        page.locator(".sandbox-review-item").first.click()
        expect(page.locator("#sandbox-evidence-popover")).to_be_visible()
        expect(page.locator("#sandbox-evidence-body")).to_contain_text("审查条件")
        assert model_calls == []
        assert tick_calls == []
    finally:
        page.close()


def test_fault_prepare_defaults_to_candidate_boundary_decision_board(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, fault]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(fault));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION],
        )

        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="domcontentloaded")
        board = page.locator('[data-decision-board="fault-prepare"]')
        expect(board).to_be_visible()
        expect(board.locator(".fault-decision-card")).to_have_count(3)
        expect(board.locator('[data-fault-card="candidate"] h2')).to_have_text("候选状态")
        expect(board.locator('[data-fault-card="boundary"] h2')).to_have_text("边界确认")
        expect(board.locator('[data-fault-card="next"] h2')).to_have_text("下一步")
        expect(board.locator("#fault-decision-candidate-summary")).to_have_text("1 场景 · 1 注入点")
        expect(board.locator("#fault-decision-boundary-summary")).to_have_text("0/2 已回答")
        expect(board.locator("#fault-decision-next-action")).to_contain_text("需完成边界确认")
        expect(page.locator("#fault-candidate-matrix-panel")).to_be_visible()
        expect(page.locator("#fault-candidate-matrix-count")).to_have_text("1 行")
        expect(page.locator("#fault-candidate-matrix-body [data-fault-matrix-row]")).to_have_count(1)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint33-row='fault-matrix']")).to_have_count(1)
        expect(page.locator("#fault-candidate-matrix-body .blueprint-row--fault-matrix")).to_have_count(1)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-row-pattern='shared-v1']")).to_have_count(1)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-col]")).to_have_count(9)
        assert page.locator("#fault-candidate-matrix-body .fault-matrix-path-token").count() >= 2
        assert page.locator("#fault-candidate-matrix-body .blueprint-row-token").count() >= 3
        expect(page.locator("#fault-candidate-matrix-body")).to_contain_text("RA 输入")
        expect(page.locator("#fault-candidate-matrix-body .fault-matrix-injection-cell").first).not_to_contain_text("input_ra")
        expect(page.locator("#fault-candidate-matrix-body [data-raw-node-id='input_ra']")).to_have_text("RA 输入")
        expect(page.locator("#fault-candidate-details")).to_be_visible()
        expect(page.locator("#fault-injection-point-details")).to_be_visible()
        assert page.locator("#fault-candidate-details").evaluate("element => element.open") is False
        assert page.locator("#fault-injection-point-details").evaluate("element => element.open") is False

        board_box = board.bounding_box()
        assert board_box is not None
        assert board_box["height"] <= 132
        boundary_list_box = page.locator("#fault-boundary-list").bounding_box()
        action_strip_box = page.locator("#fault-bottom-action-strip").bounding_box()
        assert boundary_list_box is not None
        assert action_strip_box is not None
        assert boundary_list_box["height"] <= 160
        assert boundary_list_box["y"] + boundary_list_box["height"] <= action_strip_box["y"] - 12
        textarea_heights = page.locator("textarea[data-boundary-id]").evaluate_all(
            "nodes => nodes.map((node) => node.getBoundingClientRect().height)"
        )
        assert textarea_heights and all(height <= 64 for height in textarea_heights)

        for index in range(page.locator("textarea[data-boundary-id]").count()):
            page.locator("textarea[data-boundary-id]").nth(index).fill("确认空跑演示边界。")
        expect(board.locator("#fault-decision-boundary-summary")).to_have_text("2/2 已回答")
        expect(board.locator("#fault-decision-next-action")).to_contain_text("可进入沙盒")
        expect(board.locator("#fault-decision-next-action")).to_contain_text("候选矩阵")
        expect(page.locator("#fault-sandbox-next")).to_be_enabled()
    finally:
        page.close()


def test_fault_prepare_boundary_confirmation_copy_wraps_at_1280(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 820})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, fault]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(fault));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION],
        )

        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="networkidle")
        boundary_copy_boxes = page.locator(
            "#fault-boundary-list .fault-boundary-item strong, "
            "#fault-boundary-list .fault-boundary-item p"
        ).evaluate_all(
            """nodes => nodes.map((node) => ({
              scrollWidth: node.scrollWidth,
              clientWidth: node.clientWidth,
              scrollHeight: node.scrollHeight,
              clientHeight: node.clientHeight,
            }))"""
        )
        assert len(boundary_copy_boxes) == 4
        assert all(box["scrollWidth"] <= box["clientWidth"] + 1 for box in boundary_copy_boxes)
        assert all(box["scrollHeight"] <= box["clientHeight"] + 1 for box in boundary_copy_boxes)
        assert page.locator("#fault-boundary-list").evaluate(
            "node => node.scrollHeight <= node.clientHeight + 1"
        ) is True
        boundary_list_box = page.locator("#fault-boundary-list").bounding_box()
        action_strip_box = page.locator("#fault-bottom-action-strip").bounding_box()
        assert boundary_list_box is not None
        assert action_strip_box is not None
        assert boundary_list_box["y"] + boundary_list_box["height"] <= action_strip_box["y"] - 4
    finally:
        page.close()


def test_fault_prepare_closed_reference_summaries_stay_compact_at_1366(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, fault]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(fault));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION],
        )

        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="networkidle")
        candidate = page.locator("#fault-candidate-details")
        injection_points = page.locator("#fault-injection-point-details")
        boundary_list = page.locator("#fault-boundary-list")
        action_strip = page.locator("#fault-bottom-action-strip")
        expect(candidate).to_be_visible()
        expect(injection_points).to_be_visible()
        assert candidate.evaluate("element => element.open") is False
        assert injection_points.evaluate("element => element.open") is False
        candidate_box = candidate.bounding_box()
        point_box = injection_points.bounding_box()
        boundary_box = boundary_list.bounding_box()
        action_box = action_strip.bounding_box()
        assert candidate_box is not None
        assert point_box is not None
        assert boundary_box is not None
        assert action_box is not None
        assert candidate_box["height"] <= 66
        assert point_box["height"] <= 66
        assert abs(candidate_box["y"] - point_box["y"]) <= 1
        assert candidate_box["y"] + candidate_box["height"] <= boundary_box["y"] - 6
        assert point_box["y"] + point_box["height"] <= boundary_box["y"] - 6
        assert boundary_box["y"] + boundary_box["height"] <= action_box["y"] - 4
        for selector in [
            "#fault-candidate-details > summary",
            "#fault-injection-point-details > summary",
        ]:
            assert page.locator(selector).evaluate(
                "el => el.scrollHeight <= el.clientHeight + 1"
            )
    finally:
        page.close()


def test_fault_prepare_next_action_cue_fits_at_1280(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 820})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, fault]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(fault));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION],
        )

        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="networkidle")
        next_action = page.locator("#fault-decision-next-action")
        decision_board = page.locator("#fault-decision-board")
        for index in range(page.locator("textarea[data-boundary-id]").count()):
            page.locator("textarea[data-boundary-id]").nth(index).fill("确认空跑演示边界。")
        expect(next_action).to_be_visible()
        expect(next_action).to_contain_text("可进入沙盒")
        assert next_action.evaluate(
            "el => el.scrollWidth <= el.clientWidth + 1 && el.scrollHeight <= el.clientHeight + 1"
        )
        assert next_action.evaluate("el => getComputedStyle(el).whiteSpace === 'normal'")
        board_box = decision_board.bounding_box()
        assert board_box is not None
        assert board_box["height"] <= 72
        effect_boxes = page.locator("#fault-candidate-matrix-body .fault-matrix-effect span").evaluate_all(
            """nodes => nodes.map((node) => ({
              scrollHeight: node.scrollHeight,
              clientHeight: node.clientHeight,
            }))"""
        )
        assert effect_boxes
        assert all(box["scrollHeight"] <= box["clientHeight"] + 1 for box in effect_boxes)
    finally:
        page.close()


def test_narrow_logic_builder_prioritizes_canvas_and_stream_before_engineering_rail(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 900, "height": 760})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        board_box = page.locator("#logic-detail-decision-board").bounding_box()
        stream_box = page.locator("#logic-drawing-stream-timeline").bounding_box()
        canvas_box = page.locator("#logic-canvas").bounding_box()
        rail_box = page.locator("#logic-engineering-rail").bounding_box()
        assert board_box is None
        assert stream_box is not None
        assert canvas_box is not None
        assert rail_box is not None
        assert stream_box["y"] < canvas_box["y"]
        assert canvas_box["y"] < rail_box["y"]
        assert canvas_box["y"] < 580
    finally:
        page.close()


def test_narrow_fault_prepare_prioritizes_decision_board_before_sidebar(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 900, "height": 760})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, fault]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(fault));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION],
        )

        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="domcontentloaded")
        board_box = page.locator("#fault-decision-board").bounding_box()
        sidebar_box = page.locator(".fault-sidebar").bounding_box()
        candidate_box = page.locator("#fault-candidate-details").bounding_box()
        assert board_box is not None
        assert sidebar_box is not None
        assert candidate_box is not None
        assert board_box["y"] < sidebar_box["y"]
        assert board_box["y"] < candidate_box["y"]
        assert board_box["y"] < 760
    finally:
        page.close()


def test_narrow_fault_sandbox_prioritizes_review_gates_before_long_lists(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 900, "height": 760})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )

        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="domcontentloaded")
        gate_panel_box = page.locator(".sandbox-review-gate-panel").bounding_box()
        sidebar_box = page.locator(".sandbox-sidebar").bounding_box()
        details_box = page.locator("#fault-sandbox-detail-groups").bounding_box()
        revision_button_box = page.locator("#fault-sandbox-revision-next").bounding_box()
        assert gate_panel_box is not None
        assert sidebar_box is not None
        assert details_box is not None
        assert revision_button_box is not None
        assert revision_button_box["y"] < 760
        assert gate_panel_box["y"] < sidebar_box["y"]
        assert gate_panel_box["y"] < details_box["y"]
        assert gate_panel_box["y"] < 760
    finally:
        page.close()


def test_narrow_four_step_pages_share_first_screen_density(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 900, "height": 760})
    pages = [
        ("/requirements-intake", "#requirements-preflight-panel", 220),
        ("/logic-builder", "#logic-canvas", 580),
        ("/fault-injection-prepare", "#fault-decision-board", 300),
        ("/fault-injection-sandbox", ".sandbox-review-gate-panel", 220),
    ]
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, fault, sandbox]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(fault));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandbox));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION, _dense_sandbox_plan()],
        )

        strip_heights: list[float] = []
        for path, first_screen_selector, max_first_screen_height in pages:
            page.goto(f"{demo_server}{path}", wait_until="networkidle")
            if path == "/logic-builder":
                _show_logic_builder_workbench(page)
            strip_box = page.locator('[data-command-strip="deepseek-step"]').bounding_box()
            first_screen_box = page.locator(first_screen_selector).bounding_box()
            control_heights = page.locator(
                '[data-command-strip="deepseek-step"] select, '
                '[data-command-strip="deepseek-step"] button'
            ).evaluate_all("(nodes) => nodes.map((node) => node.getBoundingClientRect().height)")
            overflow_count = page.evaluate(
                """() => Array.from(document.querySelectorAll("body *")).filter((el) => {
                  const style = window.getComputedStyle(el);
                  return style.display !== "none"
                    && el.scrollWidth > el.clientWidth + 1
                    && style.overflowX !== "hidden";
                }).length"""
            )
            assert strip_box is not None
            assert first_screen_box is not None
            assert strip_box["height"] <= 116, path
            max_first_screen_y = 580 if path == "/logic-builder" else 500
            assert first_screen_box["y"] <= max_first_screen_y, path
            assert first_screen_box["height"] <= max_first_screen_height, path
            assert all(height <= 34 for height in control_heights), path
            assert overflow_count == 0, path
            strip_heights.append(strip_box["height"])

        assert max(strip_heights) - min(strip_heights) <= 48
    finally:
        page.close()


def test_phase1_blueprint_shell_defaults_fit_1366x768(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    pages = [
        "/requirements-intake",
        "/logic-builder",
        "/fault-injection-prepare",
        "/fault-injection-sandbox",
    ]
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, fault, sandbox]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(fault));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandbox));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION, _dense_sandbox_plan()],
        )

        for path in pages:
            page.goto(f"{demo_server}{path}", wait_until="networkidle")
            assert page.evaluate("() => Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)") <= 768, path
            strip_box = page.locator('[data-command-strip="deepseek-step"]').bounding_box()
            assert strip_box is not None
            assert strip_box["height"] <= 118, path

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        expect(page.locator("#logic-page-system-strip")).to_be_visible()
        _show_logic_builder_workbench(page)
        shell = page.locator(".logic-shell")
        expect(shell).to_have_attribute("data-blueprint-phase", "phase-1-shell")
        expect(page.locator("#logic-page-system-strip")).to_be_visible()
        expect(page.locator("#logic-collapsed-tool-rail")).to_be_visible()
        expect(page.locator("#logic-right-inspector-rail")).to_be_visible()
        expect(page.locator("#logic-bottom-run-strip")).to_be_visible()
        expect(page.locator("#logic-mode-dock [data-logic-mode]")).to_have_count(5)
        expect(page.locator("#logic-mode-dock button")).to_have_count(5)
        expect(page.locator("#logic-mode-dock #logic-command-palette-open")).to_have_count(0)
        expect(page.locator("#logic-command-palette-open")).to_be_visible()
        expect(page.locator("#logic-mode-dock")).to_be_visible()
        expect(page.locator("#logic-primary-annotate")).to_be_visible()
        expect(page.locator("#logic-primary-annotate")).to_have_text("标注")
        expect(page.locator("#logic-primary-annotate")).to_have_attribute("data-primary-annotation-action", "true")
        annotate_box = page.locator("#logic-primary-annotate").bounding_box()
        assert annotate_box is not None
        assert annotate_box["width"] <= 112
        assert annotate_box["height"] <= 36
        expect(page.locator("#logic-run-parameter-drawer")).to_be_hidden()
        expect(page.locator("#logic-object-context-drawer")).to_be_hidden()
        expect(page.locator("#logic-command-palette")).to_be_hidden()
        left_rail_geometry = page.locator(".logic-inspector").evaluate(
            """el => {
              const style = getComputedStyle(el);
              const rect = el.getBoundingClientRect();
              return {height: rect.height, opacity: style.opacity, pointerEvents: style.pointerEvents};
            }"""
        )
        assert left_rail_geometry["height"] <= 1 or left_rail_geometry["opacity"] == "0"
        assert left_rail_geometry["pointerEvents"] == "none"
        assert shell.evaluate("el => !el.classList.contains('is-left-open') && !el.classList.contains('is-right-open')")

        page.click('#logic-collapsed-tool-rail [data-panel-toggle="left"]')
        assert shell.evaluate("el => el.classList.contains('is-left-open')")
        collapsed_left_rail_geometry = page.locator("#logic-collapsed-tool-rail").evaluate(
            """el => {
              const style = getComputedStyle(el);
              return {visibility: style.visibility, opacity: style.opacity, pointerEvents: style.pointerEvents};
            }"""
        )
        assert collapsed_left_rail_geometry == {"visibility": "hidden", "opacity": "0", "pointerEvents": "none"}
        status_summary_fit = page.locator("#logic-circuit-status-summary").evaluate(
            """el => ({
              scrollHeight: el.scrollHeight,
              clientHeight: el.clientHeight,
              overflowY: getComputedStyle(el).overflowY,
            })"""
        )
        assert status_summary_fit["scrollHeight"] <= status_summary_fit["clientHeight"] + 1
        assert status_summary_fit["overflowY"] == "visible"
        page.click('#logic-right-inspector-rail [data-panel-toggle="right"]')
        assert shell.evaluate("el => el.classList.contains('is-right-open')")
        expect(page.locator("#logic-object-context-drawer")).to_be_visible()

        page.click("#logic-primary-annotate")
        expect(page.locator("#logic-annotation-submit-bar")).to_be_visible()
        annotation_bar_box = page.locator("#logic-annotation-submit-bar").bounding_box()
        topbar_box = page.locator("#logic-page-system-strip").bounding_box()
        bottom_strip_box = page.locator("#logic-bottom-run-strip").bounding_box()
        assert annotation_bar_box is not None
        assert topbar_box is not None
        assert bottom_strip_box is not None
        assert annotation_bar_box["y"] >= topbar_box["y"] + topbar_box["height"] + 8
        assert annotation_bar_box["y"] + annotation_bar_box["height"] <= bottom_strip_box["y"] - 8
        expect(page.locator("#logic-annotation-submit-state")).to_contain_text("提交给 Agent")
        page.click("#logic-command-palette-open")
        expect(page.locator("#logic-command-palette")).to_be_visible()
        page.click('[data-command-close-panels="true"]')
        assert shell.evaluate("el => !el.classList.contains('is-left-open') && !el.classList.contains('is-right-open')")
        expect(page.locator("#logic-run-parameter-drawer")).to_be_hidden()
        expect(page.locator("#logic-object-context-drawer")).to_be_hidden()
        expect(page.locator("#logic-command-palette")).to_be_hidden()
    finally:
        page.close()


def test_logic_builder_requirement_trace_panel_links_source_to_canvas(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing]) => {
              localStorage.clear();
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing()],
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        expect(page.locator("#logic-output-visible-status")).to_have_attribute("data-output-visible-status", "idle")
        trace_panel = page.locator("#logic-requirement-trace-panel")
        canvas_source = page.locator("#logic-canvas-source")
        canvas_source_state = page.locator("#logic-canvas-source-state")
        canvas_trace_legend = page.locator("#logic-canvas-trace-legend")
        expect(trace_panel).to_be_visible()
        expect(page.locator("#logic-requirement-trace-source")).to_have_text("deepseek-v4-pro-demo-requirements.md")
        expect(canvas_source).to_be_visible()
        expect(canvas_source_state).to_contain_text("来源")
        expect(canvas_trace_legend).to_be_visible()
        expect(canvas_trace_legend).to_have_attribute("data-canvas-trace-legend", "ready")
        canvas_source_box = canvas_source.bounding_box()
        assert canvas_source_box is not None
        assert canvas_source_box["width"] <= 180
        trust_spine = page.locator("#logic-trust-spine")
        trust_review_state = page.locator("#logic-trust-review-state")
        expect(trust_spine).to_be_visible()
        expect(trust_spine).to_have_attribute("data-current-stage", "review")
        _assert_layout_target_uncovered(page, "#logic-requirement-trace-panel")
        _assert_layout_target_uncovered(page, "#logic-canvas")
        _assert_layout_target_uncovered(page, "#logic-trust-spine")
        expect(page.locator("#logic-trust-spine [data-trust-stage]")).to_have_count(4)
        expect(page.locator('#logic-trust-spine [data-trust-stage="review"]')).to_have_class(re.compile("is-active"))
        expect(page.locator("#logic-trust-parse-state")).to_contain_text("段原文已结构化")
        expect(page.locator("#logic-trust-map-state")).to_contain_text("段落到节点/连线")
        expect(trust_review_state).to_contain_text("节点 /")
        _expect_trust_review_consistency(
            trust_review_state,
            state="segment-only",
            review_id="row-logic1",
            current_id="row-logic1",
            selected_id="none",
        )
        _expect_trust_spine_consistency(
            trust_spine,
            state="segment-only",
            current_id="row-logic1",
            selected_id="none",
        )
        expect(page.locator("#logic-trust-source-state")).to_contain_text("需求页交接已接收")
        review_matrix = page.locator("#logic-global-review-matrix")
        expect(review_matrix).to_be_visible()
        expect(review_matrix.locator("[data-review-item]")).to_have_count(4)
        expect(review_matrix).to_have_attribute("data-node-count", "20")
        expect(review_matrix).to_have_attribute("data-wire-count", "23")
        expect(review_matrix.locator('[data-review-item="logic"]')).to_have_attribute("data-review-status", "pass")
        expect(review_matrix.locator("[data-review-filter-action]")).to_have_count(4)
        expect(review_matrix.locator('[data-review-filter-action="source"]')).to_be_visible()
        expect(review_matrix.locator('[data-review-filter-action="assumption"]')).to_be_visible()
        expect(review_matrix.locator('[data-review-filter-action="local"]')).to_be_visible()
        expect(review_matrix.locator('[data-review-filter-action="all"]')).to_be_visible()
        expect(page.locator("#logic-review-logic-count")).to_have_text("20 / 23")
        expect(page.locator("#logic-review-assumption-state")).to_contain_text("候选假设")
        expect(page.locator("#logic-review-local-state")).to_contain_text("本地补齐")
        review_matrix.locator('[data-review-filter-action="assumption"]').click()
        expect(page.locator("#logic-canvas")).to_have_attribute("data-provenance-filter", "assumption")
        expect(review_matrix.locator('[data-review-filter-action="assumption"]')).to_have_attribute("aria-pressed", "true")
        expect(page.locator("#logic-output-visible-status")).to_have_attribute("data-output-visible-status", "view")
        expect(page.locator("#logic-output-visible-status")).to_have_attribute("data-output-visible-target-id", "assumption")
        expect(page.locator("#logic-output-visible-status")).to_have_attribute("data-output-visible-verification-source", "view-action")
        review_matrix.locator('[data-review-filter-action="local"]').click()
        expect(page.locator("#logic-canvas")).to_have_attribute("data-provenance-filter", "local")
        expect(review_matrix.locator('[data-review-filter-action="local"]')).to_have_attribute("aria-pressed", "true")
        expect(page.locator("#logic-output-visible-status")).to_have_attribute("data-output-visible-status", "view")
        expect(page.locator("#logic-output-visible-status")).to_have_attribute("data-output-visible-target-id", "local")
        expect(page.locator("#logic-output-visible-status")).to_have_attribute("data-output-visible-verification-source", "view-action")
        review_matrix.locator('[data-review-filter-action="all"]').click()
        expect(page.locator("#logic-canvas")).to_have_attribute("data-provenance-filter", "all")
        expect(review_matrix.locator('[data-review-filter-action="all"]')).to_have_attribute("aria-pressed", "true")
        expect(page.locator("#logic-output-visible-status")).to_have_attribute("data-output-visible-status", "view")
        expect(page.locator("#logic-output-visible-status")).to_have_attribute("data-output-visible-target-id", "all")
        expect(page.locator("#logic-output-visible-status")).to_have_attribute("data-output-visible-verification-source", "view-action")
        trace_items = page.locator("#logic-requirement-trace-list [data-requirement-trace-id]")
        expect(trace_items).to_have_count(4)
        expect(page.locator("#logic-requirement-trace-list .logic-requirement-trace-item.is-active")).to_have_count(1)
        first_trace_impact = trace_items.nth(0).locator(".logic-requirement-trace-output-impacts")
        second_trace_impact = trace_items.nth(1).locator(".logic-requirement-trace-output-impacts")
        expect(first_trace_impact).to_be_visible()
        expect(second_trace_impact).to_be_visible()
        expect(first_trace_impact).to_have_attribute("data-output-impact-state", "ready")
        expect(second_trace_impact).to_have_attribute("data-output-impact-state", "ready")
        expect(first_trace_impact).to_contain_text("TLS")
        expect(second_trace_impact).to_contain_text("ETRAC")
        assert first_trace_impact.inner_text() != second_trace_impact.inner_text()
        assert first_trace_impact.locator(".logic-output-impact-badge").count() <= 3
        assert second_trace_impact.locator(".logic-output-impact-badge").count() <= 3
        output_backtrace = page.locator("#logic-output-backtrace-panel")
        expect(output_backtrace).to_be_visible()
        expect(output_backtrace).to_have_attribute("data-output-backtrace", "ready")
        expect(output_backtrace).to_have_attribute("data-output-total-count", "4")
        expect(output_backtrace).to_have_attribute("data-output-covered-count", "4")
        expect(output_backtrace).to_have_attribute("data-output-coverage-status", "pass")
        output_focus_status = page.locator("#logic-output-focus-status")
        expect(output_focus_status).to_have_count(1)
        expect(output_focus_status).to_have_class(re.compile("logic-output-focus-status"))
        expect(output_focus_status).to_have_attribute("aria-live", "polite")
        expect(output_focus_status).to_have_attribute("aria-atomic", "true")
        expect(output_focus_status).to_have_attribute("role", "status")
        output_visible_status = page.locator("#logic-output-visible-status")
        expect(output_visible_status).to_have_count(1)
        expect(output_visible_status).to_be_visible()
        expect(output_visible_status).to_have_class(re.compile("logic-output-visible-status"))
        expect(output_visible_status).to_have_attribute("aria-hidden", "true")
        expect(output_visible_status).to_have_attribute("data-output-visible-status", "view")
        expect(output_visible_status).to_have_attribute("data-output-visible-target-kind", "view")
        expect(output_visible_status).to_have_attribute("data-output-visible-target-id", "all")
        expect(output_visible_status).to_have_attribute("data-output-visible-verification", "verified")
        expect(output_visible_status).to_have_attribute("data-output-visible-verification-source", "view-action")
        expect(output_visible_status).to_contain_text("全局复核视图")
        assert page.evaluate("""() => {
          const panel = document.querySelector("#logic-output-backtrace-panel");
          const status = document.querySelector("#logic-output-focus-status");
          return Boolean(panel && status && status.parentElement === panel);
        }""") is True
        assert page.evaluate("""() => {
          const coverage = document.querySelector("#logic-output-backtrace-coverage");
          const visibleStatus = document.querySelector("#logic-output-visible-status");
          const hiddenStatus = document.querySelector("#logic-output-focus-status");
          return Boolean(coverage && visibleStatus && hiddenStatus
            && visibleStatus.previousElementSibling === coverage
            && visibleStatus.nextElementSibling === hiddenStatus);
        }""") is True
        assert page.evaluate("""() => {
          const status = document.querySelector("#logic-output-focus-status");
          if (!status) return false;
          const box = status.getBoundingClientRect();
          const style = window.getComputedStyle(status);
          return style.position === "absolute" && box.width <= 1 && box.height <= 1;
        }""") is True
        expect(output_backtrace.locator("[data-output-backtrace-output]")).to_have_count(4)
        assert page.locator('#logic-output-backtrace-list [data-source-count]:not([data-source-count="0"])').count() >= 3
        expect(output_backtrace.locator('[data-output-backtrace-output="tls"]')).to_contain_text("段 01")
        expect(output_backtrace.locator('[data-output-backtrace-output="etrac"]')).to_contain_text("段 02")
        expect(output_backtrace.locator('[data-output-backtrace-output="deploy"]')).to_contain_text("段 03")
        expect(output_backtrace.locator(".logic-output-backtrace-evidence")).to_have_count(4)
        expect(output_backtrace.locator('[data-output-backtrace-output="tls"] .logic-output-backtrace-evidence')).to_contain_text("段")
        expect(output_backtrace.locator('[data-output-backtrace-output="tls"] .logic-output-backtrace-evidence')).to_contain_text("线索")
        output_coverage = page.locator("#logic-output-backtrace-coverage")
        expect(output_coverage).to_be_visible()
        expect(output_coverage).to_contain_text("输出 4/4")
        expect(output_coverage).to_contain_text("当前")
        expect(output_coverage).to_contain_text("TLS")
        first_output_coverage_text = output_coverage.inner_text()
        assert_output_backtrace_list_focus_ring = """() => {
          const list = document.querySelector("#logic-output-backtrace-list");
          if (!list || document.activeElement !== list) return false;
          const style = window.getComputedStyle(list);
          return style.outlineStyle !== "none"
            && parseFloat(style.outlineWidth) >= 1
            && style.outlineColor !== "rgba(0, 0, 0, 0)"
            && style.boxShadow !== "none";
        }"""
        assert_output_backtrace_related_focus_ring = """() => {
          const item = document.querySelector('#logic-output-backtrace-list .logic-output-backtrace-item.is-related[role="button"]');
          if (!item || document.activeElement !== item) return false;
          const style = window.getComputedStyle(item);
          return style.outlineStyle !== "none"
            && parseFloat(style.outlineWidth) >= 1
            && style.outlineColor !== "rgba(0, 0, 0, 0)";
        }"""
        segment_card = page.locator("#logic-current-segment-evidence")
        segment_source_cue = page.locator("#logic-current-segment-source-cue")
        segment_consistency = page.locator("#logic-current-segment-consistency")
        segment_consistency_cue = page.locator("#logic-current-segment-consistency-cue")
        segment_consistency_align = page.locator("#logic-current-segment-consistency-align")
        segment_trust_chain = page.locator("#logic-current-segment-trust-chain")
        segment_global_review = page.locator("#logic-current-segment-global-review")
        expect(segment_card).to_be_visible()
        expect(segment_card).to_have_attribute("data-current-segment-id", "row-logic1")
        expect(segment_card).to_have_attribute("data-current-segment-selection-label", re.compile("段落"))
        assert segment_source_cue.inner_text() == (segment_card.get_attribute("data-current-segment-selection-label") or "")
        expect(segment_consistency).to_be_visible()
        _expect_trace_consistency(
            segment_consistency,
            state="segment-only",
            consistency_id="row-logic1",
            current_id="row-logic1",
            selected_id="none",
            cue="segment-only",
            cue_label="待锚点",
            alignable=False,
        )
        expect(segment_consistency_cue).to_be_visible()
        expect(segment_consistency_cue).to_have_attribute("data-trace-consistency-cue", "segment-only")
        _assert_current_segment_consistency_cue_layout(page, align_visible=False)
        _expect_consistency_align_button(segment_consistency_align, visible=False, enabled=False)
        expect(segment_card).to_have_attribute("data-node-count", "5")
        expect(segment_card).to_have_attribute("data-wire-count", "4")
        expect(segment_trust_chain).to_be_visible()
        expect(segment_trust_chain).to_have_attribute("data-current-segment-trust-chain", "ready")
        expect(segment_trust_chain).to_have_attribute("data-current-segment-trace-id", "row-logic1")
        expect(segment_trust_chain).to_have_attribute("data-source-anchor-id", "logic1")
        expect(segment_trust_chain).to_have_attribute("data-node-count", "5")
        expect(segment_trust_chain).to_have_attribute("data-wire-count", "4")
        expect(segment_trust_chain).to_have_attribute("data-output-count", re.compile(r"^[1-9]"))
        expect(segment_trust_chain).to_have_attribute("data-review-anchor-count", "10")
        expect(segment_trust_chain).to_have_attribute("data-current-segment-trust-chain-scope", "current-segment")
        expect(segment_trust_chain).to_have_attribute("title", re.compile("当前段.*链路"))
        expect(segment_trust_chain).to_have_attribute("aria-label", re.compile("当前段.*链路"))
        expect(segment_trust_chain.locator("[data-trust-chain-step]")).to_have_count(4)
        expect(segment_trust_chain.locator('[data-trust-chain-step="source"]')).to_contain_text("段 01")
        expect(segment_trust_chain.locator('[data-trust-chain-step="source"]')).to_contain_text("读取")
        expect(segment_trust_chain.locator('[data-trust-chain-step="map"]')).to_contain_text("5 节点")
        expect(segment_trust_chain.locator('[data-trust-chain-step="map"]')).to_contain_text("4 连线")
        expect(segment_trust_chain.locator('[data-trust-chain-step="output"]')).to_contain_text("TLS")
        expect(segment_trust_chain.locator('[data-trust-chain-step="review"]')).to_contain_text("10 锚点复核")
        expect(segment_global_review).to_be_visible()
        expect(segment_global_review).to_have_attribute("data-global-review-state", "ready")
        expect(segment_global_review).to_have_attribute("data-global-review-scope", "current-segment-to-global")
        expect(segment_global_review).to_have_attribute("data-current-segment-id", "row-logic1")
        expect(segment_global_review).to_have_attribute("data-output-count", re.compile(r"^[1-9]"))
        expect(segment_global_review).to_have_attribute("data-review-anchor-count", re.compile(r"^[1-9]"))
        expect(segment_global_review).to_have_attribute("title", re.compile("全局复核.*全局矩阵"))
        expect(segment_global_review).to_have_attribute("aria-label", re.compile("全局复核.*当前段"))
        expect(segment_global_review).to_contain_text("全局复核闭环")
        expect(segment_global_review).to_contain_text("当前段到全局矩阵")
        expect(segment_global_review).to_contain_text("当前段")
        expect(segment_global_review).to_contain_text("全局矩阵")
        _expect_current_segment_identity_loop_state(
            page,
            state="segment-only",
            current_id="row-logic1",
            selected_id="none",
            selected_source="none",
            source_anchor_id="logic1",
        )
        expect(page.locator("#logic-canvas")).to_be_visible()
        _assert_current_segment_trust_chain_layout(page)
        expect(page.locator("#logic-current-segment-title")).to_contain_text("段 01")
        expect(page.locator("#logic-current-segment-anchor")).to_contain_text("节点")
        expect(page.locator("#logic-current-segment-review")).to_contain_text("全局复核")
        output_impact = page.locator("#logic-current-segment-output-impact")
        expect(output_impact).to_be_visible()
        expect(output_impact).to_have_attribute("data-output-impact", "ready")
        expect(output_impact).to_have_attribute("data-output-impact-count", re.compile(r"^[1-9]"))
        expect(output_impact).to_have_attribute("data-output-impact-labels", re.compile("TLS"))
        expect(output_impact).to_have_attribute("data-output-impact-visible-labels", re.compile(r"^[^|]+(\\|[^|]+){0,2}$"))
        expect(output_impact).to_have_attribute("data-output-impact-source", "trace-output-map")
        expect(output_impact).to_have_attribute("aria-label", re.compile("最终输出影响摘要"))
        expect(output_impact).to_have_attribute("title", re.compile("TLS"))
        expect(page.locator("#logic-current-segment-output-labels")).to_contain_text("TLS")
        first_output_impact = page.locator("#logic-current-segment-output-labels").inner_text()
        first_output_impact_labels = output_impact.get_attribute("data-output-impact-labels") or ""
        first_output_impact_visible_labels = output_impact.get_attribute("data-output-impact-visible-labels") or ""
        first_output_impact_label_list = [label for label in first_output_impact_labels.split("|") if label]
        first_output_impact_visible_list = [label for label in first_output_impact_visible_labels.split("|") if label]
        first_output_impact_count = int(output_impact.get_attribute("data-output-impact-count") or "0")
        first_output_impact_title = output_impact.get_attribute("title") or ""
        first_output_impact_aria = output_impact.get_attribute("aria-label") or ""
        assert first_output_impact_count == len(first_output_impact_label_list)
        assert 1 <= len(first_output_impact_visible_list) <= 3
        assert len(first_output_impact.split(" · ")) <= 3
        if len(first_output_impact_label_list) > 2:
            assert first_output_impact_visible_list[-1] == f"+{len(first_output_impact_label_list) - 2}"
            assert first_output_impact_visible_list[-1] in first_output_impact
        else:
            assert not any(label.startswith("+") for label in first_output_impact_visible_list)
        for label in first_output_impact_label_list:
            assert label in first_output_impact_title
            assert label in first_output_impact_aria
        output_reveal = page.locator("#logic-current-segment-output-reveal")
        expect(output_reveal).to_have_count(1)
        related_output_focus = output_backtrace.locator('.logic-output-backtrace-item.is-related[role="button"]').first
        if len(first_output_impact_label_list) > 2:
            expect(output_reveal).to_be_visible()
            expect(output_reveal).to_be_enabled()
            expect(output_reveal).to_have_attribute("data-output-impact-reveal", "ready")
            expect(output_reveal).to_have_attribute("data-hidden-output-count", str(len(first_output_impact_label_list) - 2))
            expect(output_reveal).to_have_attribute("data-target-trace-id", "row-logic1")
            expect(output_reveal).to_have_attribute("aria-controls", "logic-output-backtrace-panel")
            expect(output_reveal).to_have_attribute("aria-expanded", "false")
            expect(output_reveal).to_have_attribute("aria-label", re.compile("输出回溯完整清单"))
            output_reveal.click()
            expect(output_backtrace).to_be_visible()
            expect(output_backtrace).to_have_attribute("data-current-segment-output-reveal", "active")
            expect(output_backtrace).to_have_attribute("data-reveal-trace-id", "row-logic1")
            expect(output_backtrace).to_have_attribute("data-reveal-source", "current-segment-output-summary")
            expect(output_backtrace).to_have_attribute("data-output-focus-feedback", "none")
            expect(output_reveal).to_have_attribute("aria-expanded", "true")
            expect(output_focus_status).to_contain_text("已展开")
            expect(output_focus_status).to_contain_text("全部输出依据")
            expect(output_focus_status).to_contain_text("段 01")
            assert "row-logic" not in output_focus_status.inner_text()
            expect(output_visible_status).to_have_attribute("data-output-visible-status", "expanded")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-kind", "requirement-trace")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-id", "row-logic1")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification", "verified")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification-source", "reveal-trace")
            expect(output_visible_status).to_contain_text("已展开")
            expect(output_visible_status).to_contain_text("全部输出依据")
            expect(output_visible_status).to_contain_text("段 01")
            assert "row-logic" not in output_visible_status.inner_text()
            assert page.evaluate("""() => {
              const visibleStatus = document.querySelector("#logic-output-visible-status");
              const hiddenStatus = document.querySelector("#logic-output-focus-status");
              const panel = document.querySelector("#logic-output-backtrace-panel");
              return Boolean(visibleStatus && hiddenStatus && panel
                && visibleStatus.textContent === hiddenStatus.textContent
                && visibleStatus.dataset.outputVisibleTargetId === panel.dataset.revealTraceId);
            }""") is True
            expect(related_output_focus).to_be_focused()
            assert page.evaluate(assert_output_backtrace_related_focus_ring) is True
            expect(output_backtrace.locator(".logic-output-backtrace-item.is-related")).not_to_have_count(0)
            expect(page.locator("#logic-canvas")).to_be_visible()
            output_backtrace.locator('[data-output-backtrace-output="tls"]').click()
            expect(output_backtrace).to_have_attribute("data-current-segment-output-reveal", "none")
            expect(output_backtrace).to_have_attribute("data-reveal-trace-id", "")
            expect(output_backtrace).to_have_attribute("data-reveal-source", "")
            expect(output_reveal).to_have_attribute("aria-expanded", "false")
            expect(output_backtrace).to_have_attribute("data-active-output", "tls")
            expect(output_backtrace.locator('[data-output-backtrace-output="tls"]')).to_be_focused()
            expect(output_focus_status).to_contain_text("已聚焦")
            expect(output_focus_status).to_contain_text("TLS")
            expect(output_visible_status).to_have_attribute("data-output-visible-status", "focused")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-kind", "output")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-id", "tls")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification", "verified")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification-source", "active-output")
            expect(output_visible_status).to_contain_text("已聚焦")
            assert page.evaluate("""() => {
              const status = document.querySelector("#logic-output-focus-status");
              return Boolean(status && !(status.textContent.includes("已展开") && status.textContent.includes("全部输出依据")));
            }""") is True
            assert page.evaluate("""() => {
              const visibleStatus = document.querySelector("#logic-output-visible-status");
              const hiddenStatus = document.querySelector("#logic-output-focus-status");
              const panel = document.querySelector("#logic-output-backtrace-panel");
              return Boolean(visibleStatus && hiddenStatus
                && panel
                && visibleStatus.textContent === hiddenStatus.textContent
                && visibleStatus.dataset.outputVisibleTargetId === panel.dataset.activeOutput
                && !(visibleStatus.textContent.includes("已展开") && visibleStatus.textContent.includes("全部输出依据")));
            }""") is True
            assert page.evaluate("""() => {
              const panel = document.querySelector("#logic-output-backtrace-panel");
              const activeItem = document.querySelector("#logic-output-backtrace-list .logic-output-backtrace-item.is-active");
              return Boolean(panel && activeItem && activeItem.dataset.outputBacktraceOutput === panel.dataset.activeOutput);
            }""") is True
            output_reveal.click()
            expect(output_backtrace).to_have_attribute("data-current-segment-output-reveal", "active")
            expect(output_focus_status).to_contain_text("已展开")
            expect(output_focus_status).to_contain_text("全部输出依据")
            expect(output_focus_status).to_contain_text("段 01")
            expect(output_visible_status).to_have_attribute("data-output-visible-status", "expanded")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-kind", "requirement-trace")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-id", "row-logic1")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification", "verified")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification-source", "reveal-trace")
            assert "row-logic" not in output_visible_status.inner_text()
            expect(related_output_focus).to_be_focused()
        else:
            expect(output_reveal).to_be_hidden()
        segment_jumps = page.locator("#logic-current-segment-anchor-jumps")
        expect(segment_jumps).to_be_visible()
        expect(segment_jumps.locator("[data-current-segment-jump]")).to_have_count(3)
        segment_jumps.locator('[data-current-segment-jump="source"]').click()
        expect(page.locator("#logic-canvas")).to_have_attribute("data-provenance-filter", "source")
        expect(segment_jumps.locator('[data-current-segment-jump="source"]')).to_have_attribute("aria-pressed", "true")
        if len(first_output_impact_label_list) > 2:
            expect(segment_jumps.locator('[data-current-segment-jump="source"]')).to_be_focused()
            assert page.evaluate("""() => {
              const active = document.activeElement;
              return Boolean(active && !active.closest("#logic-output-backtrace-list"));
            }""") is True
            expect(output_backtrace).to_have_attribute("data-current-segment-output-reveal", "none")
            expect(output_backtrace).to_have_attribute("data-reveal-trace-id", "")
            expect(output_backtrace).to_have_attribute("data-reveal-source", "")
            expect(output_reveal).to_have_attribute("aria-expanded", "false")
            expect(output_focus_status).to_contain_text("当前段来源锚点视图")
            expect(output_visible_status).to_have_attribute("data-output-visible-status", "view")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-kind", "view")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-id", "source")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification", "verified")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification-source", "view-action")
            expect(output_visible_status).to_contain_text("当前段来源锚点视图")
            assert page.evaluate("""() => {
              const status = document.querySelector("#logic-output-focus-status");
              return Boolean(status && !(status.textContent.includes("已展开") && status.textContent.includes("全部输出依据")));
            }""") is True
            assert page.evaluate("""() => {
              const visibleStatus = document.querySelector("#logic-output-visible-status");
              const hiddenStatus = document.querySelector("#logic-output-focus-status");
              return Boolean(visibleStatus && hiddenStatus
                && visibleStatus.textContent === hiddenStatus.textContent
                && visibleStatus.dataset.outputVisibleTargetKind === "view"
                && visibleStatus.dataset.outputVisibleTargetId === "source"
                && !(visibleStatus.textContent.includes("已展开") && visibleStatus.textContent.includes("全部输出依据")));
            }""") is True
            output_reveal.focus()
            expect(output_reveal).to_be_focused()
            page.keyboard.press("Enter")
            expect(output_backtrace).to_have_attribute("data-current-segment-output-reveal", "active")
            expect(output_backtrace).to_have_attribute("data-reveal-trace-id", "row-logic1")
            expect(output_backtrace).to_have_attribute("data-output-focus-feedback", "none")
            expect(output_reveal).to_have_attribute("aria-expanded", "true")
            expect(output_focus_status).to_contain_text("已展开")
            expect(output_focus_status).to_contain_text("全部输出依据")
            expect(output_focus_status).to_contain_text("段 01")
            expect(output_visible_status).to_have_attribute("data-output-visible-status", "expanded")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-kind", "requirement-trace")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-id", "row-logic1")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification", "verified")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification-source", "reveal-trace")
            assert "row-logic" not in output_visible_status.inner_text()
            expect(related_output_focus).to_be_focused()
            assert page.evaluate(assert_output_backtrace_related_focus_ring) is True
        segment_jumps.locator('[data-current-segment-jump="trace"]').click()
        expect(page.locator("#logic-canvas")).to_have_attribute("data-provenance-filter", "all")
        expect(segment_jumps.locator('[data-current-segment-jump="trace"]')).to_have_attribute("aria-pressed", "true")
        if len(first_output_impact_label_list) > 2:
            expect(segment_jumps.locator('[data-current-segment-jump="trace"]')).to_be_focused()
            expect(output_backtrace).to_have_attribute("data-current-segment-output-reveal", "none")
            expect(output_reveal).to_have_attribute("aria-expanded", "false")
            expect(output_focus_status).to_contain_text("当前段逻辑线路视图")
            expect(output_visible_status).to_have_attribute("data-output-visible-status", "view")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-kind", "view")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-id", "trace")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification", "verified")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification-source", "view-action")
            expect(output_visible_status).to_contain_text("当前段逻辑线路视图")
            assert page.evaluate("""() => {
              const status = document.querySelector("#logic-output-focus-status");
              return Boolean(status && !(status.textContent.includes("已展开") && status.textContent.includes("全部输出依据")));
            }""") is True
            output_reveal.focus()
            expect(output_reveal).to_be_focused()
            page.keyboard.press("Space")
            expect(output_backtrace).to_have_attribute("data-current-segment-output-reveal", "active")
            expect(output_backtrace).to_have_attribute("data-reveal-trace-id", "row-logic1")
            expect(output_reveal).to_have_attribute("aria-expanded", "true")
            expect(output_focus_status).to_contain_text("已展开")
            expect(output_focus_status).to_contain_text("全部输出依据")
            expect(output_focus_status).to_contain_text("段 01")
            expect(output_visible_status).to_have_attribute("data-output-visible-status", "expanded")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-kind", "requirement-trace")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-id", "row-logic1")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification", "verified")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification-source", "reveal-trace")
            assert "row-logic" not in output_visible_status.inner_text()
            expect(related_output_focus).to_be_focused()
            assert page.evaluate(assert_output_backtrace_related_focus_ring) is True
        expect(page.locator(".logic-circuit-node.is-requirement-trace-match")).not_to_have_count(0)
        segment_jumps.locator('[data-current-segment-jump="all"]').click()
        expect(page.locator("#logic-canvas")).to_have_attribute("data-provenance-filter", "all")
        expect(segment_jumps.locator('[data-current-segment-jump="all"]')).to_have_attribute("aria-pressed", "true")
        if len(first_output_impact_label_list) > 2:
            expect(segment_jumps.locator('[data-current-segment-jump="all"]')).to_be_focused()
            expect(output_backtrace).to_have_attribute("data-current-segment-output-reveal", "none")
            expect(output_focus_status).to_contain_text("全局复核视图")
            expect(output_visible_status).to_have_attribute("data-output-visible-status", "view")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-kind", "view")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-id", "all")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification", "verified")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification-source", "view-action")
            expect(output_visible_status).to_contain_text("全局复核视图")
            assert page.evaluate("""() => {
              const status = document.querySelector("#logic-output-focus-status");
              return Boolean(status && !(status.textContent.includes("已展开") && status.textContent.includes("全部输出依据")));
            }""") is True
            assert page.evaluate("""() => {
              const visibleStatus = document.querySelector("#logic-output-visible-status");
              const hiddenStatus = document.querySelector("#logic-output-focus-status");
              return Boolean(visibleStatus && hiddenStatus
                && visibleStatus.textContent === hiddenStatus.textContent
                && visibleStatus.dataset.outputVisibleTargetKind === "view"
                && visibleStatus.dataset.outputVisibleTargetId === "all"
                && !(visibleStatus.textContent.includes("已展开") && visibleStatus.textContent.includes("全部输出依据")));
            }""") is True
        active_trace = page.locator("#logic-requirement-trace-list .logic-requirement-trace-item.is-active")
        expect(active_trace).to_have_attribute("data-source-anchor-id", "logic1")
        active_text = active_trace.inner_text()
        assert "读取" in active_text
        assert "生成" in active_text
        for internal_token in ["radio_altitude_ft", "reverser_inhibited", "tls115"]:
            assert internal_token not in active_text
        review_summary = page.locator("#logic-requirement-trace-review-summary").inner_text()
        assert "原文锚点" in review_summary
        assert "候选假设" in review_summary
        assert "本地补齐" in review_summary
        expect(page.locator(".logic-circuit-node.is-requirement-trace-match")).not_to_have_count(0)
        second_trace_labels = second_trace_impact.get_attribute("data-output-impact-labels") or ""
        etrac_backtrace_source = output_backtrace.locator('[data-output-backtrace-output="etrac"] [data-output-backtrace-source="row-logic2"]')
        etrac_backtrace_source_box = etrac_backtrace_source.bounding_box()
        assert etrac_backtrace_source_box is not None
        etrac_backtrace_source.focus()
        expect(etrac_backtrace_source).to_be_focused()
        etrac_backtrace_source.evaluate("(button) => button.click()")
        expect(segment_card).to_have_attribute("data-current-segment-id", "row-logic2")
        expect(page.locator("#logic-current-segment-title")).to_contain_text("段 02")
        expect(segment_trust_chain).to_have_attribute("data-current-segment-trace-id", "row-logic2")
        expect(segment_trust_chain).to_have_attribute("data-output-count", re.compile(r"^[1-9]"))
        expect(segment_trust_chain.locator('[data-trust-chain-step="source"]')).to_contain_text("段 02")
        expect(segment_trust_chain.locator('[data-trust-chain-step="output"]')).to_contain_text("ETRAC")
        expect(segment_trust_chain.locator('[data-trust-chain-step="review"]')).to_contain_text("锚点复核")
        expect(segment_global_review).to_have_attribute("data-current-segment-id", "row-logic2")
        expect(segment_global_review).to_contain_text("当前段到全局矩阵")
        expect(segment_global_review).to_contain_text("当前段")
        expect(segment_global_review).to_contain_text("全局矩阵")
        _assert_current_segment_trust_chain_layout(page)
        expect(output_impact).to_have_attribute("data-output-impact-labels", re.compile("ETRAC"))
        assert (output_impact.get_attribute("data-output-impact-labels") or "") != first_output_impact_labels
        assert (output_impact.get_attribute("data-output-impact-visible-labels") or "") != first_output_impact_visible_labels
        second_output_impact_label_list = [label for label in (output_impact.get_attribute("data-output-impact-labels") or "").split("|") if label]
        second_output_impact_visible_list = [label for label in (output_impact.get_attribute("data-output-impact-visible-labels") or "").split("|") if label]
        assert int(output_impact.get_attribute("data-output-impact-count") or "0") == len(second_output_impact_label_list)
        assert 1 <= len(second_output_impact_visible_list) <= 3
        if len(second_output_impact_label_list) > 2:
            expect(output_reveal).to_be_visible()
            expect(output_reveal).to_have_attribute("data-target-trace-id", "row-logic2")
            output_reveal.click()
            expect(output_backtrace).to_have_attribute("data-current-segment-output-reveal", "active")
            expect(output_backtrace).to_have_attribute("data-reveal-trace-id", "row-logic2")
            expect(output_backtrace).to_have_attribute("data-reveal-source", "current-segment-output-summary")
            expect(output_backtrace).to_have_attribute("data-output-focus-feedback", "none")
            expect(output_reveal).to_have_attribute("aria-expanded", "true")
            expect(output_focus_status).to_contain_text("已展开")
            expect(output_focus_status).to_contain_text("全部输出依据")
            expect(output_focus_status).to_contain_text("段 02")
            expect(output_visible_status).to_have_attribute("data-output-visible-status", "expanded")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-kind", "requirement-trace")
            expect(output_visible_status).to_have_attribute("data-output-visible-target-id", "row-logic2")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification", "verified")
            expect(output_visible_status).to_have_attribute("data-output-visible-verification-source", "reveal-trace")
            expect(output_visible_status).to_contain_text("全部输出依据")
            expect(output_visible_status).to_contain_text("段 02")
            assert "row-logic" not in output_focus_status.inner_text()
            assert "row-logic" not in output_visible_status.inner_text()
            assert page.evaluate("""() => {
              const visibleStatus = document.querySelector("#logic-output-visible-status");
              const hiddenStatus = document.querySelector("#logic-output-focus-status");
              const panel = document.querySelector("#logic-output-backtrace-panel");
              return Boolean(visibleStatus && hiddenStatus && panel
                && visibleStatus.textContent === hiddenStatus.textContent
                && visibleStatus.dataset.outputVisibleTargetId === panel.dataset.revealTraceId);
            }""") is True
        else:
            expect(output_reveal).to_be_hidden()
        expect(page.locator("#logic-current-segment-output-labels")).to_contain_text("ETRAC")
        assert second_trace_labels.split("|")[0] in page.locator("#logic-current-segment-output-labels").inner_text()
        assert page.locator("#logic-current-segment-output-labels").inner_text() != first_output_impact
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic2")
        expect(output_backtrace).to_have_attribute("data-active-output", "etrac")
        expect(output_backtrace).to_have_attribute("data-related-output-count", "1")
        expect(output_coverage).to_contain_text("ETRAC")
        assert output_coverage.inner_text() != first_output_coverage_text
        expect(output_backtrace.locator('[data-output-backtrace-output="etrac"]')).to_have_class(re.compile("is-active"))
        expect(output_backtrace.locator('[data-output-backtrace-output="etrac"]')).to_have_class(re.compile("is-related"))
        expect(output_backtrace.locator('[data-output-backtrace-output="etrac"] [data-output-backtrace-source="row-logic2"]')).to_have_attribute("aria-pressed", "true")
        expect(page.locator("#logic-canvas")).to_be_visible()
        expect(page.locator(".logic-circuit-wire.is-requirement-trace-match")).not_to_have_count(0)
        page.locator('[data-requirement-trace-id="row-logic3"] button').click()
        expect(output_backtrace).to_have_attribute("data-related-output-mode", "multi")
        expect(output_backtrace).to_have_attribute("data-related-output-count", "2")
        expect(output_coverage).to_have_attribute("data-current-output-mode", "multi")
        expect(output_coverage).to_contain_text("多输出")
        expect(output_coverage).to_contain_text("TLS")
        expect(output_coverage).to_contain_text("EEC/PLS/PDU")
        multi_output_state = page.evaluate("""() => {
          const panel = document.querySelector("#logic-output-backtrace-panel");
          const ids = (panel?.dataset.relatedOutputIds || "").split("|").filter(Boolean);
          const labels = (panel?.dataset.relatedOutputLabels || "").split("|").filter(Boolean);
          return {
            ok: ids.includes("tls") && ids.includes("deploy") && !ids.includes("etrac")
              && labels.includes("TLS") && labels.includes("EEC/PLS/PDU"),
            ids,
            labels,
            mode: panel?.dataset.relatedOutputMode || "",
          };
        }""")
        assert multi_output_state["ok"] is True, multi_output_state
        deploy_output = output_backtrace.locator('[data-output-backtrace-output="deploy"]')
        deploy_output_box = deploy_output.bounding_box()
        assert deploy_output_box is not None
        deploy_output.evaluate("(item) => item.click()")
        expect(output_backtrace).to_have_attribute("data-active-output", "deploy")
        expect(output_backtrace).to_have_attribute("data-related-output-mode", "multi")
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic3")
        expect(page.locator('[data-requirement-trace-id="row-logic3"]')).to_have_class(re.compile("is-active"))
        expect(deploy_output).to_have_class(re.compile("is-active"))
        expect(page.locator("#logic-canvas")).to_have_attribute("data-active-output-focus", "deploy")
        for output_node_id in ["eec_deploy", "pls_power", "pdu_motor"]:
            expect(page.locator(f'[data-demo-node-id="{output_node_id}"]')).to_have_class(re.compile("is-output-backtrace-focus"))
        expect(page.locator('[data-demo-node-id="tls115"]')).not_to_have_class(re.compile("is-output-backtrace-focus"))
        expect(page.locator('[data-wire-id="logic3->eec_deploy"]')).to_have_class(re.compile("is-output-backtrace-focus"))
        expect(page.locator(".logic-circuit-wire.is-output-backtrace-focus")).not_to_have_count(0)
        expect(page.locator(".logic-circuit-node.is-requirement-trace-match")).not_to_have_count(0)
        expect(page.locator(".logic-circuit-wire.is-requirement-trace-match")).not_to_have_count(0)
        etrac_output = output_backtrace.locator('[data-output-backtrace-output="etrac"]')
        etrac_output_box = etrac_output.bounding_box()
        assert etrac_output_box is not None
        etrac_output.evaluate("(item) => item.click()")
        expect(output_backtrace).to_have_attribute("data-active-output", "deploy")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback", "not-related")
        expect(output_backtrace).to_have_attribute("data-output-focus-blocked", "etrac")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback-label", "非当前段相关输出")
        expect(output_visible_status).to_have_attribute("data-output-visible-status", "blocked")
        expect(output_visible_status).to_have_attribute("data-output-visible-target-kind", "output")
        expect(output_visible_status).to_have_attribute("data-output-visible-target-id", "etrac")
        expect(output_visible_status).to_have_attribute("data-output-visible-verification", "verified")
        expect(output_visible_status).to_have_attribute("data-output-visible-verification-source", "blocked-output")
        expect(output_visible_status).to_contain_text("非当前段相关输出")
        assert page.evaluate("""() => {
          const visibleStatus = document.querySelector("#logic-output-visible-status");
          const hiddenStatus = document.querySelector("#logic-output-focus-status");
          const panel = document.querySelector("#logic-output-backtrace-panel");
          return Boolean(visibleStatus && hiddenStatus && panel
            && visibleStatus.textContent === hiddenStatus.textContent
            && visibleStatus.dataset.outputVisibleTargetId === panel.dataset.outputFocusBlocked);
        }""") is True
        expect(etrac_output).to_have_attribute("data-output-focus-feedback-label", "非当前段相关输出")
        expect(etrac_output).to_have_attribute("aria-label", re.compile("非当前段相关输出"))
        expect(etrac_output).to_have_attribute("title", re.compile("非当前段相关输出"))
        expect(etrac_output).to_have_class(re.compile("is-output-focus-blocked"))
        expect(output_focus_status).to_contain_text("ETRAC")
        expect(output_focus_status).to_contain_text("非当前段相关输出")
        first_noop_status = output_focus_status.inner_text()
        etrac_output.evaluate("(item) => item.click()")
        expect(output_focus_status).to_contain_text("非当前段相关输出")
        assert output_focus_status.inner_text() != first_noop_status
        expect(page.locator("#logic-canvas")).to_have_attribute("data-active-output-focus", "deploy")
        expect(page.locator('[data-demo-node-id="tls115"]')).not_to_have_class(re.compile("is-output-backtrace-focus"))
        expect(page.locator('[data-wire-id="logic3->eec_deploy"]')).to_have_class(re.compile("is-output-backtrace-focus"))
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic3")
        tls_output = output_backtrace.locator('[data-output-backtrace-output="tls"]')
        tls_output.focus()
        page.keyboard.press("Enter")
        expect(output_backtrace).to_have_attribute("data-active-output", "tls")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback", "none")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback-label", "")
        expect(etrac_output).not_to_have_attribute("data-output-focus-feedback-label", "非当前段相关输出")
        expect(etrac_output).to_have_attribute("title", "聚焦 ETRAC 输出组")
        expect(etrac_output).not_to_have_class(re.compile("is-output-focus-blocked"))
        expect(output_focus_status).to_contain_text("TLS")
        assert "非当前段相关输出" not in output_focus_status.inner_text()
        expect(page.locator("#logic-canvas")).to_have_attribute("data-active-output-focus", "tls")
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic3")
        eec_node = page.locator('[data-demo-node-id="eec_deploy"]')
        eec_node_box = eec_node.bounding_box()
        assert eec_node_box is not None
        page.mouse.click(eec_node_box["x"] + eec_node_box["width"] / 2, eec_node_box["y"] + eec_node_box["height"] / 2)
        expect(output_backtrace).to_have_attribute("data-active-output", "deploy")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback", "none")
        expect(page.locator("#logic-canvas")).to_have_attribute("data-active-output-focus", "deploy")
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic3")
        expect(eec_node).to_have_class(re.compile("is-selected"))
        canvas_backlink_state = page.evaluate("""() => {
          const panel = document.querySelector("#logic-output-backtrace-panel");
          const ids = (panel?.dataset.relatedOutputIds || "").split("|").filter(Boolean);
          return {
            ok: ids.includes("tls") && ids.includes("deploy") && !ids.includes("etrac"),
            ids,
            activeOutput: panel?.dataset.activeOutput || "",
          };
        }""")
        assert canvas_backlink_state["ok"] is True, canvas_backlink_state
        etrac_output.focus()
        page.keyboard.press("Enter")
        expect(output_backtrace).to_have_attribute("data-active-output", "deploy")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback", "not-related")
        expect(output_backtrace).to_have_attribute("data-output-focus-blocked", "etrac")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback-label", "非当前段相关输出")
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic3")
        deploy_output.focus()
        page.keyboard.press(" ")
        expect(output_backtrace).to_have_attribute("data-active-output", "deploy")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback", "none")
        expect(etrac_output).not_to_have_class(re.compile("is-output-focus-blocked"))
        expect(page.locator("#logic-canvas")).to_have_attribute("data-active-output-focus", "deploy")
        etrac_output.focus()
        page.keyboard.press(" ")
        expect(output_backtrace).to_have_attribute("data-active-output", "deploy")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback", "not-related")
        expect(output_backtrace).to_have_attribute("data-output-focus-blocked", "etrac")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback-label", "非当前段相关输出")
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic3")
        deploy_output.focus()
        page.keyboard.press("Enter")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback", "none")
        expect(etrac_output).not_to_have_class(re.compile("is-output-focus-blocked"))
        const_etrac_node = page.locator('[data-demo-node-id="etrac_540v"]')
        const_etrac_node_box = const_etrac_node.bounding_box()
        assert const_etrac_node_box is not None
        page.mouse.click(const_etrac_node_box["x"] + const_etrac_node_box["width"] / 2, const_etrac_node_box["y"] + const_etrac_node_box["height"] / 2)
        expect(output_backtrace).to_have_attribute("data-active-output", "deploy")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback", "not-related")
        expect(output_backtrace).to_have_attribute("data-output-focus-blocked", "etrac")
        expect(etrac_output).to_have_class(re.compile("is-output-focus-blocked"))
        expect(page.locator("#logic-canvas")).to_have_attribute("data-active-output-focus", "deploy")
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic3")
        expect(output_backtrace.locator('[data-output-backtrace-output="tls"]')).to_have_class(re.compile("is-related"))
        expect(deploy_output).to_have_class(re.compile("is-related"))
        expect(output_backtrace.locator('[data-output-backtrace-output="etrac"]')).not_to_have_class(re.compile("is-active|is-related"))
        page.locator('[data-requirement-trace-id="row-logic2"] button').click()
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic2")
        expect(segment_card).to_have_attribute("data-current-segment-id", "row-logic2")
        expect(output_backtrace).to_have_attribute("data-active-output", "etrac")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback", "none")
        expect(output_backtrace).to_have_attribute("data-output-focus-blocked", "")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback-label", "")
        expect(etrac_output).not_to_have_class(re.compile("is-output-focus-blocked"))
        expect(etrac_output).to_have_class(re.compile("is-active"))
        expect(etrac_output).to_have_class(re.compile("is-related"))
        expect(output_coverage).to_contain_text("ETRAC")
        expect(page.locator("#logic-canvas")).to_have_attribute("data-active-output-focus", "etrac")
        expect(page.locator(".logic-circuit-node.is-requirement-trace-match")).not_to_have_count(0)

        trace_panel_box = trace_panel.bounding_box()
        trace_list_box = page.locator("#logic-requirement-trace-list").bounding_box()
        output_backtrace_box = output_backtrace.bounding_box()
        output_coverage_box = output_coverage.bounding_box()
        output_visible_status_box = output_visible_status.bounding_box()
        output_backtrace_list_box = page.locator("#logic-output-backtrace-list").bounding_box()
        segment_card_box = segment_card.bounding_box()
        review_matrix_box = review_matrix.bounding_box()
        canvas_box = page.locator("#logic-canvas").bounding_box()
        toolbar_box = page.locator("#logic-canvas-compact-toolbar").bounding_box()
        bottom_strip_box = page.locator("#logic-bottom-run-strip").bounding_box()
        assert trace_panel_box is not None
        assert trace_list_box is not None
        assert output_backtrace_box is not None
        assert output_coverage_box is not None
        assert output_visible_status_box is not None
        assert output_backtrace_list_box is not None
        assert segment_card_box is not None
        assert review_matrix_box is not None
        assert canvas_box is not None
        assert toolbar_box is not None
        assert bottom_strip_box is not None
        assert trace_list_box["height"] >= 100
        assert output_visible_status_box["width"] <= output_backtrace_box["width"]
        assert output_visible_status_box["height"] <= 24
        assert output_backtrace_list_box["height"] >= 16
        assert output_coverage_box["y"] - 4 <= output_visible_status_box["y"]
        assert output_visible_status_box["y"] <= output_coverage_box["y"] + output_coverage_box["height"] + 8
        assert output_coverage_box["y"] - 4 <= output_backtrace_list_box["y"]
        assert abs((output_visible_status_box["y"] + output_visible_status_box["height"]) - output_backtrace_list_box["y"]) <= 28
        assert output_visible_status_box["x"] >= output_backtrace_box["x"] - 1
        assert output_visible_status_box["x"] + output_visible_status_box["width"] <= output_backtrace_box["x"] + output_backtrace_box["width"] + 1
        assert output_visible_status_box["x"] >= output_coverage_box["x"] - 2
        assert output_visible_status_box["x"] >= output_backtrace_box["x"] + 42
        assert output_visible_status_box["x"] + output_visible_status_box["width"] <= output_coverage_box["x"] + output_coverage_box["width"] + 2
        assert page.evaluate("""() => {
          const status = document.querySelector("#logic-output-visible-status");
          const canvas = document.querySelector("#logic-canvas");
          const list = document.querySelector("#logic-output-backtrace-list");
          if (!status || !canvas || !list) return false;
          const overlap = (a, b) => {
            const ar = a.getBoundingClientRect();
            const br = b.getBoundingClientRect();
            return ar.left < br.right && ar.right > br.left && ar.top < br.bottom && ar.bottom > br.top;
          };
          return !overlap(status, canvas) && !overlap(status, list);
        }""") is True
        assert page.evaluate("""() => {
          const status = document.querySelector("#logic-output-visible-status");
          if (!status) return false;
          const style = window.getComputedStyle(status);
          return style.whiteSpace === "nowrap"
            && style.overflowX === "hidden"
            && style.textOverflow === "ellipsis"
            && status.getClientRects().length === 1;
        }""") is True
        assert page.evaluate("""() => Array.from(document.querySelectorAll("#logic-output-backtrace-list [data-output-backtrace-output]")).every((item) => Number(item.dataset.sourceCount || "0") >= 0 && Number(item.dataset.wireCount || "0") >= 0)""") is True
        hidden_source_index_state = page.evaluate("""() => {
          const etrac = document.querySelector('[data-output-backtrace-output="etrac"]');
          if (!etrac) return { ok: false, reason: "missing-etrac" };
          const clonedSource = document.createElement("button");
          clonedSource.type = "button";
          clonedSource.className = "logic-output-backtrace-source";
          clonedSource.dataset.outputBacktraceSource = "row-logic3";
          clonedSource.textContent = "段 03";
          clonedSource.hidden = true;
          etrac.appendChild(clonedSource);
          document.querySelector('[data-requirement-trace-id="row-logic3"] button')?.click();
          const panel = document.querySelector("#logic-output-backtrace-panel");
          const coverage = document.querySelector("#logic-output-backtrace-coverage");
          const relatedIds = (panel?.dataset.relatedOutputIds || "").split("|").filter(Boolean);
          const ok = relatedIds.includes("deploy")
            && !relatedIds.includes("etrac")
            && Number(panel?.dataset.relatedOutputCount || "0") >= 1
            && coverage?.textContent.includes("EEC/PLS/PDU")
            && !etrac.classList.contains("is-related");
          const result = {
            ok,
            activeOutput: panel?.dataset.activeOutput || "",
            relatedOutputCount: panel?.dataset.relatedOutputCount || "",
            relatedOutputIds: panel?.dataset.relatedOutputIds || "",
            coverage: coverage?.textContent || "",
            etracClass: etrac.className || "",
          };
          clonedSource.remove();
          return result;
        }""")
        assert hidden_source_index_state["ok"] is True, hidden_source_index_state
        assert page.evaluate("""() => {
          const coverage = document.querySelector("#logic-output-backtrace-coverage");
          const panel = document.querySelector("#logic-output-backtrace-panel");
          return Boolean(coverage && panel && coverage.scrollWidth <= coverage.clientWidth + 1 && panel.scrollWidth <= panel.clientWidth + 1);
        }""") is True
        assert page.evaluate("""() => Array.from(document.querySelectorAll("#logic-requirement-trace-list .logic-requirement-trace-item button")).every((button) => button.scrollWidth <= button.clientWidth + 1 && button.scrollHeight <= button.clientHeight + 1)""") is True
        assert trace_list_box["y"] + trace_list_box["height"] + 4 <= segment_card_box["y"]
        assert segment_card_box["y"] + segment_card_box["height"] + 4 <= output_backtrace_box["y"]
        assert output_backtrace_box["y"] + output_backtrace_box["height"] <= review_matrix_box["y"] + 1
        assert segment_card_box["y"] + segment_card_box["height"] <= review_matrix_box["y"] + 1
        assert review_matrix_box["y"] + review_matrix_box["height"] <= trace_panel_box["y"] + trace_panel_box["height"] + 1
        assert trace_panel_box["x"] + trace_panel_box["width"] <= canvas_box["x"] - 8
        assert toolbar_box["x"] >= canvas_box["x"] - 1
        assert bottom_strip_box["x"] >= canvas_box["x"] - 1
        assert canvas_box["width"] >= 860
        assert page.evaluate("() => document.scrollingElement.scrollWidth <= window.innerWidth") is True

        page.locator('[data-requirement-trace-id="row-logic3"] button').click()
        expect(page.locator('[data-requirement-trace-id="row-logic3"]')).to_have_class(re.compile("is-active"))
        expect(trust_spine).to_have_attribute("data-active-trace-id", "row-logic3")
        expect(page.locator('[data-demo-node-id="logic3"]')).to_have_class(re.compile("is-requirement-trace-match"))
        expect(segment_card).to_have_attribute("data-current-segment-selection-label", re.compile("段落"))
        assert segment_source_cue.inner_text() == (segment_card.get_attribute("data-current-segment-selection-label") or "")
        expect(page.locator('[data-demo-node-id="logic2"]')).to_have_attribute("data-canvas-trace-selectable", "true")
        expect(page.locator('[data-wire-id="sw1->logic1"]')).to_have_attribute("data-canvas-trace-selectable", "true")
        expect(page.locator('[data-demo-node-id="etrac_540v"]')).not_to_have_attribute("data-canvas-trace-selectable", "true")
        expect(page.locator('[data-wire-id="logic2->etrac_540v"]')).not_to_have_attribute("data-canvas-trace-selectable", "true")
        page.locator('[data-wire-id="logic2->etrac_540v"]').evaluate(
            """(wire) => wire.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }))"""
        )
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic3")
        expect(trace_panel).to_have_attribute("data-active-trace-source", "trace-list")
        page.locator('[data-demo-node-id="logic2"]').click()
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic2")
        expect(trace_panel).to_have_attribute("data-active-trace-source", "canvas-node")
        expect(page.locator("#logic-current-segment-evidence")).to_have_attribute("data-current-segment-id", "row-logic2")
        expect(page.locator("#logic-current-segment-evidence")).to_have_attribute("data-current-segment-selection-source", "canvas-node")
        expect(page.locator("#logic-current-segment-evidence")).to_have_attribute("data-current-segment-selection-label", re.compile("节点.*反选"))
        assert segment_source_cue.inner_text() == (segment_card.get_attribute("data-current-segment-selection-label") or "")
        expect(page.locator('[data-requirement-trace-id="row-logic2"]')).to_have_class(re.compile("is-active"))
        expect(page.locator('[data-demo-node-id="logic2"]')).to_have_class(re.compile("is-requirement-trace-match"))
        context_trace = page.locator("#logic-context-requirement-trace")
        annotation_trace = page.locator("#logic-annotation-requirement-trace")
        expect(page.locator("#logic-object-context-drawer")).to_be_visible()
        expect(page.locator("#logic-annotation-popover")).to_be_visible()
        expect(context_trace).to_be_visible()
        expect(context_trace).to_have_attribute("data-context-requirement-trace", "matched")
        expect(context_trace).to_contain_text("段")
        expect(annotation_trace).to_have_attribute("data-annotation-requirement-trace", "matched")
        _expect_cross_surface_trace_audit(
            segment_consistency=segment_consistency,
            trust_review_state=trust_review_state,
            trust_spine=trust_spine,
            context_trace=context_trace,
            annotation_trace=annotation_trace,
            state="consistent",
            consistency_id="row-logic2",
            review_id="row-logic2",
            trace_id="row-logic2",
            current_id="row-logic2",
            selected_id="row-logic2",
            selected_source="canvas-node",
            cue="consistent",
            cue_label="四表面一致",
        )
        _expect_current_segment_trust_chain_mirror(page, expected_trace_id="row-logic2")
        _expect_inspector_trace_state_badge(page, "一致")
        _expect_canvas_selected_trace_state_badge(
            page,
            "一致",
            state="consistent",
            current_id="row-logic2",
            selected_id="row-logic2",
            selected_source="canvas-node",
        )
        _expect_canvas_source_trace_state_badge(
            page,
            "一致",
            state="consistent",
            current_id="row-logic2",
            selected_id="row-logic2",
            selected_source="canvas-node",
        )
        _assert_inspector_trace_badge_layout(page, "一致")
        _expect_bridge_token_across_trace_surfaces(page)
        _expect_global_review_counts_across_trace_surfaces(page)
        _expect_trace_identity_coherence_across_surfaces(page)
        expect(segment_consistency_cue).to_have_attribute("data-trace-consistency-cue", "consistent")
        expect(trust_review_state).to_have_attribute("data-trace-consistency-review-label", "四表面一致")
        expect(annotation_trace).to_contain_text("段")
        expect(segment_consistency).to_have_attribute("data-trace-consistency-surfaces", re.compile("left.*canvas.*context.*annotation"))
        page.locator('[data-requirement-trace-id="row-logic3"] button').click()
        expect(segment_card).to_have_attribute("data-current-segment-id", "row-logic3")
        _expect_cross_surface_trace_audit(
            segment_consistency=segment_consistency,
            trust_review_state=trust_review_state,
            trust_spine=trust_spine,
            context_trace=context_trace,
            annotation_trace=annotation_trace,
            state="diverged",
            trace_id="row-logic2",
            current_id="row-logic3",
            selected_id="row-logic2",
            selected_source="canvas-node",
            cue="diverged",
            cue_label="证据分叉",
            alignable=True,
            align_target_id="row-logic2",
            align_source="canvas-node",
        )
        _expect_current_segment_identity_loop_state(
            page,
            state="diverged",
            current_id="row-logic3",
            selected_id="row-logic2",
            selected_source="canvas-node",
        )
        _expect_canvas_selected_trace_state_badge(
            page,
            "分叉",
            state="diverged",
            current_id="row-logic3",
            selected_id="row-logic2",
            selected_source="canvas-node",
        )
        _expect_canvas_source_trace_state_badge(
            page,
            "分叉",
            state="diverged",
            current_id="row-logic3",
            selected_id="row-logic2",
            selected_source="canvas-node",
        )
        expect(segment_consistency).to_have_attribute("aria-label", re.compile("diverged.*row-logic3.*row-logic2"))
        expect(segment_consistency_cue).to_have_attribute("data-trace-consistency-cue", "diverged")
        _assert_current_segment_consistency_cue_layout(page, align_visible=True)
        expect(trust_review_state).to_have_attribute("aria-label", re.compile("diverged.*row-logic3.*row-logic2"))
        expect(trust_spine).to_have_attribute("data-trace-consistency-review-label", "证据分叉")
        _expect_consistency_align_button(
            segment_consistency_align,
            visible=True,
            enabled=True,
            action="align-selected-trace",
            align="ready",
            target_id="row-logic2",
            source="canvas-node",
        )
        segment_consistency_align.click()
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic2")
        expect(trace_panel).to_have_attribute("data-active-trace-source", "canvas-node")
        expect(segment_card).to_have_attribute("data-current-segment-id", "row-logic2")
        expect(segment_card).to_have_attribute("data-current-segment-selection-source", "canvas-node")
        _expect_trace_consistency(
            segment_consistency,
            state="consistent",
            consistency_id="row-logic2",
            current_id="row-logic2",
            selected_id="row-logic2",
            cue="consistent",
            cue_label="四表面一致",
            alignable=False,
        )
        _expect_current_segment_identity_loop_state(
            page,
            state="consistent",
            current_id="row-logic2",
            selected_id="row-logic2",
            selected_source="canvas-node",
        )
        _assert_current_segment_consistency_cue_layout(page, align_visible=False)
        _expect_consistency_align_button(segment_consistency_align, visible=False, enabled=False)
        page.locator('[data-requirement-trace-id="row-logic3"] button').click()
        _expect_trace_consistency(
            segment_consistency,
            state="diverged",
            current_id="row-logic3",
            selected_id="row-logic2",
            cue="diverged",
            alignable=True,
            align_target_id="row-logic2",
            align_source="canvas-node",
        )
        _expect_consistency_align_button(
            segment_consistency_align,
            visible=True,
            enabled=True,
            action="align-selected-trace",
            align="ready",
            target_id="row-logic2",
            source="canvas-node",
        )
        segment_consistency_align.focus()
        expect(segment_consistency_align).to_be_focused()
        page.keyboard.press("Enter")
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic2")
        expect(trace_panel).to_have_attribute("data-active-trace-source", "canvas-node")
        _expect_trace_consistency(segment_consistency, state="consistent", consistency_id="row-logic2")
        _assert_current_segment_consistency_cue_layout(page, align_visible=False)
        _expect_consistency_align_button(segment_consistency_align, visible=False, enabled=False)
        expect(page.locator("#logic-canvas")).to_be_visible()
        expect(page.locator('[data-demo-node-id="logic3"]')).not_to_have_class(re.compile("is-requirement-trace-match"))
        page.locator('[data-wire-id="sw1->logic1"]').evaluate(
            """(wire) => wire.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }))"""
        )
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic1")
        expect(trace_panel).to_have_attribute("data-active-trace-source", "canvas-wire")
        expect(page.locator("#logic-current-segment-evidence")).to_have_attribute("data-current-segment-id", "row-logic1")
        expect(page.locator("#logic-current-segment-evidence")).to_have_attribute("data-current-segment-selection-source", "canvas-wire")
        expect(page.locator("#logic-current-segment-evidence")).to_have_attribute("data-current-segment-selection-label", re.compile("连线.*反选"))
        assert segment_source_cue.inner_text() == (segment_card.get_attribute("data-current-segment-selection-label") or "")
        expect(page.locator('[data-requirement-trace-id="row-logic1"]')).to_have_class(re.compile("is-active"))
        expect(page.locator('[data-wire-id="sw1->logic1"]')).to_have_attribute("data-canvas-requirement-trace-id", "row-logic1")
        expect(context_trace).to_have_attribute("data-context-requirement-trace", "matched")
        _expect_requirement_trace_audit(
            context_trace,
            prefix="context",
            trace_id="row-logic1",
            selected_source="canvas-wire",
        )
        expect(context_trace).to_contain_text("段")
        expect(context_trace).to_have_attribute("data-context-trust-chain-state", "ready")
        expect(context_trace).to_have_attribute("data-context-trust-chain-trace-id", "row-logic1")
        expect(context_trace).to_have_attribute("data-context-trust-chain-source-anchor-id", "logic1")
        expect(context_trace).to_have_attribute("data-context-trust-chain-node-count", "5")
        expect(context_trace).to_have_attribute("data-context-trust-chain-wire-count", "4")
        expect(context_trace).to_have_attribute("data-context-trust-chain-output-count", re.compile(r"^[1-9]"))
        expect(context_trace).to_have_attribute("data-context-trust-chain-review-anchor-count", "10")
        expect(context_trace).to_have_attribute("data-context-trust-chain-surface", "current-segment")
        expect(context_trace).to_have_attribute("data-context-trust-chain-scope", "current-segment")
        expect(annotation_trace).to_have_attribute("data-annotation-requirement-trace", "matched")
        _expect_requirement_trace_audit(
            annotation_trace,
            prefix="annotation",
            trace_id="row-logic1",
            selected_source="canvas-wire",
        )
        expect(annotation_trace).to_contain_text("段")
        expect(annotation_trace).to_have_attribute("data-annotation-trust-chain-state", "ready")
        expect(annotation_trace).to_have_attribute("data-annotation-trust-chain-trace-id", "row-logic1")
        expect(annotation_trace).to_have_attribute("data-annotation-trust-chain-source-anchor-id", "logic1")
        expect(annotation_trace).to_have_attribute("data-annotation-trust-chain-node-count", "5")
        expect(annotation_trace).to_have_attribute("data-annotation-trust-chain-wire-count", "4")
        expect(annotation_trace).to_have_attribute("data-annotation-trust-chain-output-count", re.compile(r"^[1-9]"))
        expect(annotation_trace).to_have_attribute("data-annotation-trust-chain-review-anchor-count", "10")
        expect(annotation_trace).to_have_attribute("data-annotation-trust-chain-surface", "current-segment")
        expect(annotation_trace).to_have_attribute("data-annotation-trust-chain-scope", "current-segment")
        _expect_current_segment_trust_chain_mirror(page, expected_trace_id="row-logic1")
        assert page.evaluate("""() => {
          const context = document.querySelector("#logic-context-requirement-trace");
          const annotation = document.querySelector("#logic-annotation-requirement-trace");
          if (!context || !annotation) return false;
          const check = (element, prefix) => {
            const tail = window.getComputedStyle(element, "::after").content || "";
            const outputCount = Number.parseInt(element.dataset[`${prefix}TrustChainOutputCount`] || "0", 10);
            const reviewAnchorCount = Number.parseInt(element.dataset[`${prefix}TrustChainReviewAnchorCount`] || "0", 10);
            const counts = tail.match(/段链\\s*(\\d+)输出\\/(\\d+)全局复核/) || [];
            return tail.includes("段链")
              && tail.includes("输出")
              && tail.includes("全局复核")
              && Number.parseInt(counts[1] || "-1", 10) === outputCount
              && Number.parseInt(counts[2] || "-1", 10) === reviewAnchorCount;
          };
          return check(context, "context") && check(annotation, "annotation");
        }""") is True
        _expect_trace_consistency(segment_consistency, state="consistent", consistency_id="row-logic1")
        _assert_current_segment_consistency_cue_layout(page, align_visible=False)
        _expect_trust_review_consistency(trust_review_state, state="consistent", review_id="row-logic1")
        page.locator('[data-requirement-trace-id="row-logic3"] button').click()
        _expect_requirement_trace_audit(
            context_trace,
            prefix="context",
            state="diverged",
            current_id="row-logic3",
            selected_id="row-logic1",
            selected_source="canvas-wire",
        )
        _expect_requirement_trace_audit(
            annotation_trace,
            prefix="annotation",
            state="diverged",
            current_id="row-logic3",
            selected_id="row-logic1",
            selected_source="canvas-wire",
        )
        _expect_trace_consistency(
            segment_consistency,
            state="diverged",
            current_id="row-logic3",
            selected_id="row-logic1",
            selected_source="canvas-wire",
            alignable=True,
            align_target_id="row-logic1",
            align_source="canvas-wire",
        )
        _expect_current_segment_trust_chain_mirror(page, expected_trace_id="row-logic3")
        _expect_inspector_trace_state_badge(page, "分叉")
        _expect_canvas_selected_trace_state_badge(
            page,
            "分叉",
            state="diverged",
            current_id="row-logic3",
            selected_id="row-logic1",
            selected_source="canvas-wire",
        )
        _expect_canvas_source_trace_state_badge(
            page,
            "分叉",
            state="diverged",
            current_id="row-logic3",
            selected_id="row-logic1",
            selected_source="canvas-wire",
        )
        _assert_inspector_trace_badge_layout(page, "分叉")
        _assert_current_segment_consistency_cue_layout(page, align_visible=True)
        _expect_consistency_align_button(
            segment_consistency_align,
            visible=True,
            enabled=True,
            action="align-selected-trace",
            align="ready",
            target_id="row-logic1",
            source="canvas-wire",
        )
        segment_consistency_align.focus()
        expect(segment_consistency_align).to_be_focused()
        page.keyboard.press(" ")
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic1")
        expect(trace_panel).to_have_attribute("data-active-trace-source", "canvas-wire")
        expect(segment_card).to_have_attribute("data-current-segment-id", "row-logic1")
        expect(segment_card).to_have_attribute("data-current-segment-selection-source", "canvas-wire")
        expect(segment_consistency).to_have_attribute("data-trace-consistency-state", "consistent")
        expect(segment_consistency).to_have_attribute("data-trace-consistency-id", "row-logic1")
        expect(segment_consistency).to_have_attribute("data-trace-consistency-alignable", "false")
        _expect_consistency_align_button(segment_consistency_align, visible=False, enabled=False)
        page.locator('[data-demo-node-id="etrac_540v"]').click()
        expect(context_trace).to_have_attribute("data-context-requirement-trace", "unbound")
        expect(annotation_trace).to_have_attribute("data-annotation-requirement-trace", "unbound")
        _expect_cross_surface_trace_audit(
            segment_consistency=segment_consistency,
            trust_review_state=trust_review_state,
            trust_spine=trust_spine,
            context_trace=context_trace,
            annotation_trace=annotation_trace,
            state="unbound",
            consistency_id="none",
            review_id="none",
            trace_id="none",
            selected_id="none",
            selected_source="none",
            cue="unbound",
            cue_label="未绑定",
            alignable=False,
        )
        _expect_current_segment_identity_loop_state(
            page,
            state="unbound",
            current_id="row-logic1",
            selected_id="none",
            selected_source="none",
        )
        _expect_current_segment_trust_chain_mirror(page, expected_trace_id="row-logic1")
        _expect_inspector_trace_state_badge(page, "未绑定")
        _expect_canvas_selected_trace_state_badge(
            page,
            "未绑定",
            state="unbound",
            current_id="row-logic1",
            selected_id="none",
            selected_source="none",
        )
        _expect_canvas_source_trace_state_badge(
            page,
            "未绑定",
            state="unbound",
            current_id="row-logic1",
            selected_id="none",
            selected_source="none",
        )
        _assert_inspector_trace_badge_layout(page, "未绑定")
        expect(segment_consistency_cue).to_have_attribute("data-trace-consistency-cue", "unbound")
        _assert_current_segment_consistency_cue_layout(page, align_visible=False)
        _expect_consistency_align_button(segment_consistency_align, visible=False, enabled=False)
        expect(page.locator("#logic-canvas")).to_be_visible()
        page.locator('[data-requirement-trace-id="row-logic3"] button').click()
        page.locator('[data-demo-node-id="logic2"]').focus()
        page.keyboard.press("Enter")
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic2")
        expect(trace_panel).to_have_attribute("data-active-trace-source", "canvas-node")
        expect(segment_card).to_have_attribute("data-current-segment-selection-source", "canvas-node")
        expect(segment_card).to_have_attribute("data-current-segment-selection-label", re.compile("节点.*反选"))
        page.locator('[data-requirement-trace-id="row-logic3"] button').click()
        page.locator('[data-wire-id="sw1->logic1"]').focus()
        page.keyboard.press(" ")
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic1")
        expect(trace_panel).to_have_attribute("data-active-trace-source", "canvas-wire")
        expect(segment_card).to_have_attribute("data-current-segment-selection-source", "canvas-wire")
        expect(segment_card).to_have_attribute("data-current-segment-selection-label", re.compile("连线.*反选"))
    finally:
        page.close()


def test_logic_builder_requirement_trace_panel_stays_readable_at_1280(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 820})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing]) => {
              localStorage.clear();
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing()],
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        trace_panel = page.locator("#logic-requirement-trace-panel")
        trace_list = page.locator("#logic-requirement-trace-list")
        output_backtrace = page.locator("#logic-output-backtrace-panel")
        output_coverage = page.locator("#logic-output-backtrace-coverage")
        output_status = page.locator("#logic-output-visible-status")
        output_list = page.locator("#logic-output-backtrace-list")
        segment_card = page.locator("#logic-current-segment-evidence")
        review_matrix = page.locator("#logic-global-review-matrix")
        trust_spine = page.locator("#logic-trust-spine")
        segment_jumps = page.locator("#logic-current-segment-anchor-jumps")
        output_reveal = page.locator("#logic-current-segment-output-reveal")
        canvas = page.locator("#logic-canvas")

        expect(trace_panel).to_be_visible()
        expect(trace_list).to_be_visible()
        expect(trace_list.locator(".logic-requirement-trace-item.is-active")).to_have_count(1)
        expect(trace_list.locator(".logic-requirement-trace-item.is-active")).to_contain_text("L1")
        expect(trust_spine).to_be_visible()
        expect(trust_spine).to_have_attribute("data-current-stage", "review")
        expect(page.locator("#logic-trust-review-state")).to_contain_text("节点")
        expect(page.locator("#logic-current-segment-title")).to_contain_text("段 01")
        expect(page.locator("#logic-current-segment-anchor")).to_contain_text("节点")
        matched_node = page.locator('[data-demo-node-id="logic1"]')
        matched_wire = page.locator('[data-wire-id="sw1->logic1"]')
        expect(matched_node).to_have_class(re.compile("is-requirement-trace-match"))
        expect(matched_node).to_have_attribute("data-canvas-requirement-trace-id", "row-logic1")
        expect(matched_node).to_have_attribute("data-canvas-requirement-trace-evidence", re.compile("段 01"))
        expect(matched_node).to_have_attribute("data-canvas-requirement-trace-evidence", re.compile("生成 L1 控制链"))
        expect(matched_node).to_have_attribute("aria-label", re.compile("段 01"))
        expect(matched_node.locator("title")).to_contain_text("段 01")
        expect(matched_wire).to_have_class(re.compile("is-requirement-trace-match"))
        expect(matched_wire).to_have_attribute("data-canvas-requirement-trace-id", "row-logic1")
        expect(matched_wire).to_have_attribute("data-canvas-requirement-trace-evidence", re.compile("生成 L1 控制链"))
        expect(matched_wire).to_have_attribute("aria-label", re.compile("段 01"))
        expect(matched_wire.locator("title")).to_contain_text("生成 L1 控制链")
        expect(page.locator('#logic-requirement-trace-list [data-requirement-trace-id="row-logic1"]')).to_have_count(1)
        expect(page.locator('[data-canvas-requirement-trace-id="row-logic1"]')).not_to_have_count(0)
        logic2_trace_button = trace_list.locator('[data-requirement-trace-id="row-logic2"] button')
        logic2_trace_button.click()
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic2")
        expect(segment_card).to_have_attribute("data-current-segment-id", "row-logic2")
        logic2_node = page.locator('[data-demo-node-id="logic2"]')
        logic2_wire = page.locator('[data-wire-id="sw2->logic2"]')
        old_canvas_trace_cleanup = page.evaluate("""() => {
          const node = document.querySelector('[data-demo-node-id="logic1"]');
          const wire = document.querySelector('[data-wire-id="sw1->logic1"]');
          return {
            nodeTraceId: node ? node.hasAttribute("data-canvas-requirement-trace-id") : true,
            nodeTraceEvidence: node ? node.hasAttribute("data-canvas-requirement-trace-evidence") : true,
            wireTraceId: wire ? wire.hasAttribute("data-canvas-requirement-trace-id") : true,
            wireTraceEvidence: wire ? wire.hasAttribute("data-canvas-requirement-trace-evidence") : true,
          };
        }""")
        assert old_canvas_trace_cleanup == {
            "nodeTraceId": False,
            "nodeTraceEvidence": False,
            "wireTraceId": False,
            "wireTraceEvidence": False,
        }
        expect(matched_node).not_to_have_attribute("aria-label", re.compile("段 01"))
        expect(matched_node.locator("title")).not_to_contain_text("段 01")
        expect(matched_wire).not_to_have_attribute("aria-label", re.compile("段 01"))
        expect(matched_wire.locator("title")).not_to_contain_text("生成 L1 控制链")
        expect(logic2_node).to_have_class(re.compile("is-requirement-trace-match"))
        expect(logic2_node).to_have_attribute("data-canvas-requirement-trace-id", "row-logic2")
        expect(logic2_node).to_have_attribute("data-canvas-requirement-trace-evidence", re.compile("段 02"))
        expect(logic2_node).to_have_attribute("data-canvas-requirement-trace-evidence", re.compile("L2"))
        expect(logic2_node).to_have_attribute("aria-label", re.compile("段 02"))
        expect(logic2_node.locator("title")).to_contain_text("段 02")
        expect(logic2_wire).to_have_class(re.compile("is-requirement-trace-match"))
        expect(logic2_wire).to_have_attribute("data-canvas-requirement-trace-id", "row-logic2")
        expect(logic2_wire).to_have_attribute("data-canvas-requirement-trace-evidence", re.compile("段 02"))
        expect(logic2_wire).to_have_attribute("aria-label", re.compile("段 02"))
        expect(logic2_wire.locator("title")).to_contain_text("段 02")
        trace_list.locator('[data-requirement-trace-id="row-logic1"] button').click()
        expect(trace_panel).to_have_attribute("data-active-trace-id", "row-logic1")
        expect(segment_card).to_have_attribute("data-current-segment-id", "row-logic1")
        expect(output_backtrace).to_be_visible()
        expect(output_coverage).to_be_visible()
        expect(output_status).to_be_visible()
        expect(output_list).to_be_visible()
        expect(segment_card).to_be_visible()
        expect(review_matrix).to_be_visible()
        expect(segment_jumps.locator("[data-current-segment-jump]")).to_have_count(3)
        review_readability = page.evaluate("""() => {
          const shell = document.querySelector(".logic-requirement-trace-review");
          const title = document.querySelector(".logic-requirement-trace-review > strong");
          const matrixCard = document.querySelector('#logic-global-review-matrix [data-review-item="logic"]');
          const matrixValue = document.querySelector("#logic-review-logic-count");
          const matrixAction = document.querySelector('#logic-global-review-matrix [data-review-filter-action="all"]');
          const segmentCard = document.querySelector("#logic-current-segment-evidence");
          const segmentTitle = document.querySelector("#logic-current-segment-title");
          const outputImpact = document.querySelector("#logic-current-segment-output-impact");
          const outputLabels = document.querySelector("#logic-current-segment-output-labels");
          const segmentJumpButtons = Array.from(document.querySelectorAll('#logic-current-segment-anchor-jumps [data-current-segment-jump]'));
          const parseRgb = (value) => {
            const match = String(value || "").match(/rgba?\\(([^)]+)\\)/);
            if (!match) return null;
            const parts = match[1].split(",").map((part) => Number.parseFloat(part.trim()));
            const alpha = Number.isFinite(parts[3]) ? parts[3] : 1;
            return [parts[0], parts[1], parts[2], alpha];
          };
          const compose = (foreground, background) => [
            foreground[0] * foreground[3] + background[0] * (1 - foreground[3]),
            foreground[1] * foreground[3] + background[1] * (1 - foreground[3]),
            foreground[2] * foreground[3] + background[2] * (1 - foreground[3]),
            1,
          ];
          const effectiveBackground = (element) => {
            const stack = [];
            let current = element;
            while (current && current.nodeType === 1) {
              const color = parseRgb(window.getComputedStyle(current).backgroundColor);
              if (color && color[3] > 0) stack.push(color);
              current = current.parentElement;
            }
            return stack.reverse().reduce((background, foreground) => compose(foreground, background), [255, 255, 255, 1]);
          };
          const luminance = (rgb) => {
            const channels = rgb.slice(0, 3).map((value) => {
              const channel = value / 255;
              return channel <= 0.03928 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
            });
            return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
          };
          const contrast = (foreground, background) => {
            const lighter = Math.max(luminance(foreground), luminance(background));
            const darker = Math.min(luminance(foreground), luminance(background));
            return (lighter + 0.05) / (darker + 0.05);
          };
          const sampleContrast = (textElement, backgroundElement) => {
            const foreground = parseRgb(window.getComputedStyle(textElement).color);
            const background = effectiveBackground(backgroundElement || textElement);
            return foreground && background ? contrast(foreground, background) : 0;
          };
          const segmentJumpRatios = Object.fromEntries(segmentJumpButtons.map((button) => [
            `segmentJump:${button.dataset.currentSegmentJump || "unknown"}`,
            sampleContrast(button, button),
          ]));
          const ratios = {
            title: sampleContrast(title, shell),
            matrixValue: sampleContrast(matrixValue, matrixCard),
            matrixAction: sampleContrast(matrixAction, matrixAction),
            segmentTitle: sampleContrast(segmentTitle, segmentCard),
            segmentOutput: sampleContrast(outputLabels, outputImpact),
            ...segmentJumpRatios,
          };
          return { ok: Object.values(ratios).every((ratio) => ratio >= 4.5), ratios };
        }""")
        assert review_readability["ok"] is True, review_readability
        expect(canvas).to_be_visible()

        review_matrix.locator('[data-review-filter-action="source"]').click()
        expect(canvas).to_have_attribute("data-provenance-filter", "source")
        expect(output_status).to_have_attribute("data-output-visible-status", "view")
        expect(output_status).to_have_attribute("data-output-visible-target-id", "source")
        expect(output_status).to_have_attribute("data-output-visible-verification-source", "view-action")
        review_matrix.locator('[data-review-filter-action="all"]').click()
        expect(canvas).to_have_attribute("data-provenance-filter", "all")
        expect(output_status).to_have_attribute("data-output-visible-status", "view")
        expect(output_status).to_have_attribute("data-output-visible-target-kind", "view")
        expect(output_status).to_have_attribute("data-output-visible-target-id", "all")
        expect(output_status).to_have_attribute("data-output-visible-verification", "verified")
        expect(output_status).to_have_attribute("data-output-visible-verification-source", "view-action")
        expect(output_backtrace).to_have_attribute("data-output-focus-blocked", "")
        output_reveal_state = output_reveal.get_attribute("data-output-impact-reveal") or ""
        if output_reveal_state == "ready":
            expect(output_reveal).to_have_attribute("data-output-impact-reveal", "ready")
            expect(output_reveal).to_be_visible()
            expect(output_reveal).to_have_attribute("data-target-trace-id", "row-logic1")
            output_reveal.click()
            expect(output_backtrace).to_have_attribute("data-current-segment-output-reveal", "active")
            expect(output_backtrace).to_have_attribute("data-reveal-trace-id", "row-logic1")
            expect(output_status).to_have_attribute("data-output-visible-status", "expanded")
            expect(output_status).to_have_attribute("data-output-visible-target-id", "row-logic1")
            expect(output_status).to_have_attribute("data-output-visible-verification-source", "reveal-trace")
        else:
            expect(output_reveal).to_be_hidden()
        blocked_output = output_backtrace.locator('[data-output-backtrace-output="etrac"]')
        blocked_output.evaluate("(item) => item.click()")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback", "not-related")
        expect(output_backtrace).to_have_attribute("data-output-focus-blocked", "etrac")
        expect(output_status).to_have_attribute("data-output-visible-status", "blocked")
        expect(output_status).to_have_attribute("data-output-visible-target-id", "etrac")
        expect(output_status).to_have_attribute("data-output-visible-verification-source", "blocked-output")
        segment_jumps.locator('[data-current-segment-jump="source"]').click()
        expect(canvas).to_have_attribute("data-provenance-filter", "source")
        expect(segment_jumps.locator('[data-current-segment-jump="source"]')).to_have_attribute("aria-pressed", "true")
        expect(output_backtrace).to_have_attribute("data-current-segment-output-reveal", "none")
        expect(output_backtrace).to_have_attribute("data-reveal-trace-id", "")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback", "none")
        expect(output_status).to_have_attribute("data-output-visible-status", "view")
        expect(output_status).to_have_attribute("data-output-visible-target-id", "source")
        expect(output_status).to_have_attribute("data-output-visible-verification-source", "view-action")
        segment_jumps.locator('[data-current-segment-jump="trace"]').click()
        expect(canvas).to_have_attribute("data-provenance-filter", "all")
        expect(segment_jumps.locator('[data-current-segment-jump="trace"]')).to_have_attribute("aria-pressed", "true")
        expect(output_backtrace).to_have_attribute("data-current-segment-output-reveal", "none")
        expect(output_backtrace).to_have_attribute("data-output-focus-blocked", "")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback", "none")
        expect(output_status).to_have_attribute("data-output-visible-status", "view")
        expect(output_status).to_have_attribute("data-output-visible-target-id", "trace")
        expect(output_status).to_have_attribute("data-output-visible-verification-source", "view-action")
        segment_jumps.locator('[data-current-segment-jump="all"]').click()
        expect(canvas).to_have_attribute("data-provenance-filter", "all")
        expect(segment_jumps.locator('[data-current-segment-jump="all"]')).to_have_attribute("aria-pressed", "true")
        expect(output_backtrace).to_have_attribute("data-current-segment-output-reveal", "none")
        expect(output_backtrace).to_have_attribute("data-output-focus-blocked", "")
        expect(output_backtrace).to_have_attribute("data-output-focus-feedback", "none")
        expect(output_status).to_have_attribute("data-output-visible-status", "view")
        expect(output_status).to_have_attribute("data-output-visible-target-id", "all")
        expect(output_status).to_have_attribute("data-output-visible-verification-source", "view-action")
        segment_jumps.locator('[data-current-segment-jump="trace"]').focus()
        expect(segment_jumps.locator('[data-current-segment-jump="trace"]')).to_be_focused()
        assert page.evaluate("""() => {
          const button = document.querySelector('#logic-current-segment-anchor-jumps [data-current-segment-jump="trace"]');
          if (!button || document.activeElement !== button) return false;
          const style = window.getComputedStyle(button);
          return (style.outlineStyle !== "none" && parseFloat(style.outlineWidth) >= 1)
            || style.boxShadow !== "none";
        }""") is True

        layout_state = page.evaluate("""() => {
          const byId = (id) => document.querySelector(id);
          const rect = (el) => {
            const box = el?.getBoundingClientRect();
            if (!box) return null;
            return {
              left: box.left,
              right: box.right,
              top: box.top,
              bottom: box.bottom,
              width: box.width,
              height: box.height,
            };
          };
          const overlap = (a, b) => Boolean(a && b
            && a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top);
          const panel = rect(byId("#logic-output-backtrace-panel"));
          const coverage = rect(byId("#logic-output-backtrace-coverage"));
          const statusEl = byId("#logic-output-visible-status");
          const status = rect(statusEl);
          const list = rect(byId("#logic-output-backtrace-list"));
          const canvas = rect(byId("#logic-canvas"));
          const tracePanel = rect(byId("#logic-requirement-trace-panel"));
          const statusStyle = statusEl ? window.getComputedStyle(statusEl) : null;
          return {
            ok: Boolean(panel && coverage && status && list && canvas && tracePanel),
            statusInContentColumn: Boolean(panel && coverage && status
              && status.left >= coverage.left - 2
              && status.right <= coverage.right + 2),
            statusAfterCoverage: Boolean(coverage && status && status.top >= coverage.top - 2),
            statusBeforeList: Boolean(list && status && status.bottom <= list.top + 2),
            statusDoesNotOverlapList: !overlap(status, list),
            statusDoesNotOverlapCanvas: !overlap(status, canvas),
            tracePanelDoesNotOverlapCanvas: !overlap(tracePanel, canvas),
            statusKeepsSingleLinePolicy: Boolean(statusStyle
              && statusStyle.whiteSpace === "nowrap"
              && statusStyle.overflowX === "hidden"
              && statusStyle.textOverflow === "ellipsis"),
            noHorizontalScroll: document.scrollingElement.scrollWidth <= window.innerWidth + 1,
          };
        }""")
        assert layout_state["ok"] is True, layout_state
        assert layout_state["statusInContentColumn"] is True, layout_state
        assert layout_state["statusAfterCoverage"] is True, layout_state
        assert layout_state["statusBeforeList"] is True, layout_state
        assert layout_state["statusDoesNotOverlapList"] is True, layout_state
        assert layout_state["statusDoesNotOverlapCanvas"] is True, layout_state
        assert layout_state["tracePanelDoesNotOverlapCanvas"] is True, layout_state
        assert layout_state["statusKeepsSingleLinePolicy"] is True, layout_state
        assert layout_state["noHorizontalScroll"] is True, layout_state
    finally:
        page.close()


def test_panel_state_strategy_keeps_one_auxiliary_panel_open(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, fault, sandbox]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(fault));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandbox));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION, _dense_sandbox_plan()],
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        logic_shell = page.locator(".logic-shell")
        expect(logic_shell).to_have_attribute("data-panel-strategy", "single-auxiliary")
        expect(logic_shell).to_have_attribute("data-active-aux-panel", "none")
        expect(logic_shell).to_have_attribute("data-unified-inspector-state", "none")
        expect(logic_shell).to_have_attribute("data-workstation-state", "primary")
        expect(logic_shell).to_have_attribute("data-ui-skin", "codex-minimal")
        expect(logic_shell).to_have_attribute("data-blueprint-source", "selected-final-set-20260514")
        expect(logic_shell).to_have_attribute("data-left-rail-state", "collapsed")
        expect(logic_shell).to_have_attribute("data-right-inspector-state", "collapsed")
        expect(logic_shell).to_have_attribute("data-bottom-drawer-state", "closed")
        expect(logic_shell).to_have_attribute("data-command-palette-state", "closed")
        expect(page.locator("#logic-run-parameter-drawer")).to_be_hidden()
        expect(page.locator("#logic-run-parameter-drawer")).to_have_attribute("data-unified-panel-state", "closed")
        expect(page.locator("#logic-object-context-drawer")).to_be_hidden()
        expect(page.locator("#logic-object-context-drawer")).to_have_attribute("data-unified-panel-state", "closed")
        expect(page.locator("#logic-command-palette")).to_be_hidden()
        expect(page.locator("#logic-command-palette")).to_have_attribute("data-unified-panel-state", "closed")
        expect(page.locator("#logic-mode-dock [data-logic-mode]")).to_have_count(5)
        expect(page.locator("#logic-mode-dock button")).to_have_count(5)
        expect(page.locator("#logic-mode-dock #logic-command-palette-open")).to_have_count(0)
        expect(page.locator("#logic-command-palette-open")).to_be_visible()

        page.click('#logic-right-inspector-rail [data-panel-toggle="right"]')
        expect(logic_shell).to_have_attribute("data-active-aux-panel", "right-inspector")
        expect(logic_shell).to_have_attribute("data-unified-inspector-state", "right-inspector")
        expect(logic_shell).to_have_attribute("data-left-rail-state", "collapsed")
        expect(logic_shell).to_have_attribute("data-right-inspector-state", "expanded")
        expect(logic_shell).to_have_attribute("data-bottom-drawer-state", "closed")
        expect(logic_shell).to_have_attribute("data-command-palette-state", "closed")
        expect(page.locator("#logic-object-context-drawer")).to_be_visible()
        expect(page.locator("#logic-object-context-drawer")).to_have_attribute("data-unified-panel-state", "open")
        expect(page.locator("#logic-run-parameter-drawer")).to_be_hidden()
        right_rail_geometry = page.locator("#logic-right-inspector-rail").evaluate(
            """el => {
              const style = getComputedStyle(el);
              return {visibility: style.visibility, opacity: style.opacity, pointerEvents: style.pointerEvents};
            }"""
        )
        assert right_rail_geometry == {"visibility": "hidden", "opacity": "0", "pointerEvents": "none"}

        page.click('#logic-mode-dock [data-logic-mode="parameters"]')
        expect(logic_shell).to_have_attribute("data-active-aux-panel", "bottom-drawer")
        expect(logic_shell).to_have_attribute("data-unified-inspector-state", "bottom-drawer")
        expect(logic_shell).to_have_attribute("data-left-rail-state", "collapsed")
        expect(logic_shell).to_have_attribute("data-right-inspector-state", "collapsed")
        expect(logic_shell).to_have_attribute("data-bottom-drawer-state", "open")
        expect(logic_shell).to_have_attribute("data-command-palette-state", "closed")
        expect(page.locator("#logic-run-parameter-drawer")).to_be_visible()
        expect(page.locator("#logic-run-parameter-drawer")).to_have_attribute("data-unified-panel-state", "open")
        expect(page.locator("#logic-object-context-drawer")).to_be_hidden()
        expect(page.locator("#logic-object-context-drawer")).to_have_attribute("data-unified-panel-state", "closed")
        assert logic_shell.evaluate("el => !el.classList.contains('is-left-open') && !el.classList.contains('is-right-open')")

        page.click("#logic-command-palette-open")
        expect(logic_shell).to_have_attribute("data-active-aux-panel", "command-palette")
        expect(logic_shell).to_have_attribute("data-unified-inspector-state", "command-palette")
        expect(logic_shell).to_have_attribute("data-left-rail-state", "collapsed")
        expect(logic_shell).to_have_attribute("data-right-inspector-state", "collapsed")
        expect(logic_shell).to_have_attribute("data-bottom-drawer-state", "closed")
        expect(logic_shell).to_have_attribute("data-command-palette-state", "open")
        expect(page.locator("#logic-command-palette")).to_be_visible()
        expect(page.locator("#logic-command-palette")).to_have_attribute("data-unified-panel-state", "open")
        expect(page.locator("#logic-run-parameter-drawer")).to_be_hidden()
        expect(page.locator("#logic-run-parameter-drawer")).to_have_attribute("data-unified-panel-state", "closed")
        expect(page.locator("#logic-object-context-drawer")).to_be_hidden()

        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="networkidle")
        fault_shell = page.locator(".fault-shell")
        expect(fault_shell).to_have_attribute("data-panel-strategy", "single-auxiliary")
        expect(fault_shell).to_have_attribute("data-active-aux-panel", "none")
        expect(fault_shell).to_have_attribute("data-unified-inspector-state", "none")
        expect(page.locator('.fault-sidebar[data-unified-inspector="right-inspector"]')).to_be_visible()
        expect(page.locator("#fault-context-popover")).to_be_hidden()
        expect(page.locator("#fault-context-popover")).to_have_attribute("data-unified-panel-state", "closed")

        page.locator("#fault-candidate-matrix-body [data-blueprint-fault-row='matrix']").first.click()
        expect(fault_shell).to_have_attribute("data-active-aux-panel", "fault-context-popover")
        expect(fault_shell).to_have_attribute("data-unified-inspector-state", "fault-context-popover")
        expect(page.locator("#fault-context-popover")).to_be_visible()
        expect(page.locator("#fault-context-popover")).to_have_attribute("data-unified-panel-state", "open")

        page.click("#fault-context-close")
        expect(fault_shell).to_have_attribute("data-active-aux-panel", "none")
        expect(fault_shell).to_have_attribute("data-unified-inspector-state", "none")
        expect(page.locator("#fault-context-popover")).to_have_attribute("data-unified-panel-state", "closed")

        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="networkidle")
        sandbox_shell = page.locator(".sandbox-shell")
        expect(sandbox_shell).to_have_attribute("data-panel-strategy", "single-auxiliary")
        expect(sandbox_shell).to_have_attribute("data-active-aux-panel", "none")
        expect(sandbox_shell).to_have_attribute("data-unified-inspector-state", "none")
        expect(page.locator('#fault-sandbox-diagnosis-inspector[data-unified-inspector="right-inspector"]')).to_be_visible()
        expect(page.locator("#fault-sandbox-detail-drawer")).to_be_hidden()
        expect(page.locator("#fault-sandbox-detail-drawer")).to_have_attribute("data-unified-panel-state", "closed")
        expect(page.locator("#sandbox-evidence-popover")).to_be_hidden()
        expect(page.locator("#sandbox-evidence-popover")).to_have_attribute("data-unified-panel-state", "closed")

        page.click("#fault-sandbox-toggle-detail-panel")
        expect(sandbox_shell).to_have_attribute("data-active-aux-panel", "detail-drawer")
        expect(sandbox_shell).to_have_attribute("data-unified-inspector-state", "detail-drawer")
        expect(page.locator("#fault-sandbox-detail-drawer")).to_be_visible()
        expect(page.locator("#fault-sandbox-detail-drawer")).to_have_attribute("data-unified-panel-state", "open")
        expect(page.locator("#sandbox-evidence-popover")).to_be_hidden()

        page.locator("#fault-sandbox-report-section-rows .sandbox-report-section-row").first.click()
        expect(sandbox_shell).to_have_attribute("data-active-aux-panel", "evidence-popover")
        expect(sandbox_shell).to_have_attribute("data-unified-inspector-state", "evidence-popover")
        expect(page.locator("#sandbox-evidence-popover")).to_be_visible()
        expect(page.locator("#sandbox-evidence-popover")).to_have_attribute("data-unified-panel-state", "open")
        expect(page.locator("#fault-sandbox-detail-drawer")).to_be_hidden()
        expect(page.locator("#fault-sandbox-detail-drawer")).to_have_attribute("data-unified-panel-state", "closed")

        page.click("#sandbox-evidence-close")
        expect(sandbox_shell).to_have_attribute("data-active-aux-panel", "none")
        expect(sandbox_shell).to_have_attribute("data-unified-inspector-state", "none")
        expect(page.locator("#sandbox-evidence-popover")).to_have_attribute("data-unified-panel-state", "closed")

        page.click('[data-sandbox-report-action="export"]')
        expect(sandbox_shell).to_have_attribute("data-active-aux-panel", "review-package")
        expect(sandbox_shell).to_have_attribute("data-unified-inspector-state", "review-package")
        expect(page.locator("#sandbox-review-package-panel")).to_be_visible()
        expect(page.locator("#sandbox-review-package-panel")).to_have_attribute("data-unified-panel-state", "open")
        expect(page.locator("#sandbox-evidence-popover")).to_be_hidden()

        page.click("#sandbox-review-package-close")
        expect(sandbox_shell).to_have_attribute("data-active-aux-panel", "none")
        expect(sandbox_shell).to_have_attribute("data-unified-inspector-state", "none")
        expect(page.locator("#sandbox-review-package-panel")).to_have_attribute("data-unified-panel-state", "closed")
    finally:
        page.close()


def test_logic_builder_blank_canvas_template_entry_can_seed_local_blueprint_candidate(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    model_calls: list[str] = []
    try:
        def reject_model_call(route: Any) -> None:
            model_calls.append(route.request.url)
            route.fulfill(status=500, content_type="application/json", body='{"error":"model_call_forbidden"}')

        page.route("**/api/requirements-intake/draw-logic", reject_model_call)

        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate("() => localStorage.clear()")
        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        expect(page.locator("#logic-page-system-strip")).to_be_visible()
        _show_logic_builder_workbench(page)
        expect(page.locator("main.logic-shell")).to_have_attribute("data-blueprint27-rhythm", "compact-canvas")
        expect(page.locator("#logic-page-system-strip")).to_have_attribute("data-blueprint27-rhythm", "compact-topband")
        strip_box = page.locator("#logic-page-system-strip").bounding_box()
        main_box = page.locator("main.logic-shell").bounding_box()
        assert strip_box is not None
        assert main_box is not None
        assert strip_box["height"] <= 84
        assert strip_box["y"] + strip_box["height"] - main_box["y"] <= 104
        expect(page.locator("#logic-mode-dock [data-logic-mode]")).to_have_count(5)
        expect(page.locator("#logic-mode-dock button")).to_have_count(5)
        expect(page.locator("#logic-mode-dock #logic-command-palette-open")).to_have_count(0)
        expect(page.locator("#logic-command-palette-open")).to_be_visible()
        expect(page.locator("#logic-command-palette")).to_be_hidden()
        expect(page.locator('#logic-template-entry[data-blueprint29-rhythm="blank-canvas-template-entry"]')).to_be_visible()
        expect(page.locator("#logic-start-blank-canvas")).to_be_visible()
        expect(page.locator("#logic-load-docx-template")).to_be_visible()
        expect(page.locator("#logic-restore-recent-sandbox")).to_be_visible()
        expect(page.locator("#logic-drawing-stream-timeline")).to_be_hidden()
        expect(page.locator("#logic-reconstruction-mode-panel")).to_be_hidden()
        expect(page.locator("#logic-annotation-submit-bar")).to_be_hidden()
        assert page.evaluate("() => Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)") <= 768

        page.click("#logic-load-docx-template")
        expect(page.locator("#logic-template-entry")).to_be_hidden()
        expect(page.locator("#logic-result-state")).to_have_text("电路图已完成绘制")
        expect(page.locator('#logic-canvas[data-view-mode="circuit"]')).to_be_visible()
        circuit_column_labels = page.locator("#logic-circuit-svg .logic-circuit-column-label")
        expect(circuit_column_labels).to_have_count(4)
        expect(circuit_column_labels.nth(0)).to_have_text("输入")
        expect(circuit_column_labels.nth(1)).to_have_text("逻辑门")
        expect(circuit_column_labels.nth(2)).to_have_text("中间节点")
        expect(circuit_column_labels.nth(3)).to_have_text("输出")
        expect(page.locator("#logic-circuit-svg .logic-circuit-footer-label")).to_have_text("DOCX 锚定的 L1-L4 控制链")
        expect(page.locator('#logic-circuit-svg .logic-circuit-badge[data-badge-id="boundary"]')).to_have_text("真值未变")
        expect(page.locator("#logic-bottom-run-node-count")).to_contain_text("节点 20/20")
        expect(page.locator("#logic-bottom-run-edge-count")).to_contain_text("连线 23/23")
        eec_deploy_node = page.locator('[data-demo-node-id="eec_deploy"]')
        pls_power_node = page.locator('[data-demo-node-id="pls_power"]')
        pdu_motor_node = page.locator('[data-demo-node-id="pdu_motor"]')
        thr_lock_node = page.locator('[data-demo-node-id="thr_lock"]')
        expect(eec_deploy_node.locator(".logic-circuit-node-title")).to_have_text("EEC部署")
        expect(pls_power_node.locator(".logic-circuit-node-title")).to_have_text("PLS供电")
        expect(pdu_motor_node.locator(".logic-circuit-node-title")).to_have_text("PDU电机")
        expect(thr_lock_node.locator(".logic-circuit-node-title")).to_have_text("油门锁释放")
        expect(eec_deploy_node).to_have_attribute("data-technical-label", re.compile("EEC 展开指令"))
        expect(pls_power_node).to_have_attribute("data-technical-label", re.compile("PLS 供电"))
        expect(pdu_motor_node).to_have_attribute("data-technical-label", re.compile("PDU 电机指令"))
        expect(thr_lock_node).to_have_attribute("data-technical-label", re.compile("THR_LOCK 释放"))
        stored = page.evaluate(
            """
            () => {
              const payload = JSON.parse(localStorage.getItem("ai-fantui-logic-builder-drawing-v1"));
              const circuitNodes = Object.fromEntries(payload.circuit_view.nodes.map((node) => [node.id, node]));
              return {
                truth_effect: payload.truth_effect,
                candidate_state: payload.candidate_state,
                certification_claim: payload.certification_claim,
                controller_truth_modified: payload.controller_truth_modified,
                node_count: payload.nodes.length,
                edge_count: payload.edges.length,
                circuit_node_count: payload.circuit_view.nodes.length,
                circuit_wire_count: payload.circuit_view.wires.length,
                logic3_quote: circuitNodes.logic3.source_anchors[0].quote_zh,
                logic4_quote: circuitNodes.logic4.source_anchors[0].quote_zh,
                eec_description: circuitNodes.eec_deploy.description_zh,
                pdu_description: circuitNodes.pdu_motor.description_zh,
                thr_lock_description: circuitNodes.thr_lock.description_zh,
              };
            }
            """
        )
        assert stored == {
            "truth_effect": "none",
            "candidate_state": "sandbox_candidate",
            "certification_claim": "none",
            "controller_truth_modified": False,
            "node_count": 20,
            "edge_count": 23,
            "circuit_node_count": 20,
            "circuit_wire_count": 23,
            "logic3_quote": "工作逻辑3：TLS/PLS 反馈满足后，驱动 EEC 展开、PLS 供电、PDU 电机。",
            "logic4_quote": "工作逻辑4：VDT 达到 90% 展开且 TRA≤-11.74°，THR_LOCK 释放。",
            "eec_description": "EEC 展开指令。",
            "pdu_description": "PDU 电机指令。",
            "thr_lock_description": "THR_LOCK 释放，DOCX L1-L4 链路末端输出。",
        }
        assert model_calls == []
    finally:
        page.close()


def test_docx_template_entry_carries_usage_path_cues_to_fault_and_sandbox(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    model_calls: list[str] = []
    tick_calls: list[str] = []
    try:
        def reject_model_call(route: Any) -> None:
            model_calls.append(route.request.url)
            route.fulfill(status=500, content_type="application/json", body='{"error":"model_call_forbidden"}')

        page.route("**/api/requirements-intake/draw-logic", reject_model_call)
        page.route("**/api/requirements-intake/prepare-fault-injection", reject_model_call)
        page.route("**/api/requirements-intake/prepare-fault-injection/sandbox", reject_model_call)
        page.route("**/api/tick", lambda route: (tick_calls.append(route.request.url), route.abort()))

        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate("() => localStorage.clear()")
        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        expect(page.locator("#logic-template-entry")).to_be_visible()
        page.click("#logic-load-docx-template")
        expect(page.locator("#logic-template-entry")).to_be_hidden()
        expect(page.locator("#logic-result-state")).to_have_text("电路图已完成绘制")
        expect(page.locator("#logic-result-summary")).to_contain_text("DOCX L1-L4")
        expect(page.locator("#logic-result-summary")).to_contain_text("界面蓝图演示")
        expect(page.locator("#logic-result-summary")).not_to_contain_text("UI 蓝图演示")
        expect(page.locator("#logic-workflow-detail")).to_contain_text("故障矩阵")
        expect(page.locator("#logic-fault-next")).to_be_enabled()

        page.click("#logic-fault-next")
        page.wait_for_url("**/fault-injection-prepare")
        expect(page.locator("#fault-result-state")).to_have_text("候选已生成")
        expect(page.locator("#fault-result-summary")).to_contain_text("DOCX L1-L4 模板候选")
        expect(page.locator("#fault-source-title")).to_have_text("DOCX L1-L4 模板候选")
        expect(page.locator("#fault-source-summary")).to_contain_text("来自逻辑复制页")
        expect(page.locator("#fault-source-summary")).not_to_contain_text("未发现已保存图纸")
        expect(page.locator("#fault-injection-workflow-stage")).to_have_text("DOCX 模板候选")
        expect(page.locator("#fault-injection-workflow-detail")).to_contain_text("仅候选态故障矩阵和沙盒入口")
        expect(page.locator("#fault-decision-next-action")).to_contain_text("可进入沙盒")
        expect(page.locator("#fault-decision-next-action")).to_contain_text("候选矩阵")
        expect(page.locator("#fault-decision-next-action")).to_contain_text("证据链和报告预览")
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint33-row='fault-matrix']")).to_have_count(2)
        expect(page.locator("#fault-sandbox-next")).to_be_enabled()

        template_contract = page.evaluate(
            """() => {
              const fault = JSON.parse(localStorage.getItem("ai-fantui-fault-injection-preparation-v1"));
              const sandbox = JSON.parse(localStorage.getItem("ai-fantui-fault-injection-sandbox-plan-v1"));
              return {
                fault: {
                  template_preview: fault.template_preview,
                  first_visit_preview: Boolean(fault.first_visit_preview),
                  candidate_state: fault.candidate_state,
                  truth_effect: fault.truth_effect,
                  certification_claim: fault.certification_claim,
                  controller_truth_modified: fault.controller_truth_modified,
                  source_status: fault.source_scope && fault.source_scope.fault_injection && fault.source_scope.fault_injection.status,
                },
                sandbox: {
                  template_preview: sandbox.template_preview,
                  first_visit_preview: Boolean(sandbox.first_visit_preview),
                  candidate_state: sandbox.candidate_state,
                  truth_effect: sandbox.truth_effect,
                  certification_claim: sandbox.certification_claim,
                  controller_truth_modified: sandbox.controller_truth_modified,
                  execution_contract: sandbox.execution_contract,
                },
              };
            }"""
        )
        assert template_contract == {
            "fault": {
                "template_preview": True,
                "first_visit_preview": False,
                "candidate_state": "fault_injection_preparation",
                "truth_effect": "none",
                "certification_claim": "none",
                "controller_truth_modified": False,
                "source_status": "ui_template_preview",
            },
            "sandbox": {
                "template_preview": True,
                "first_visit_preview": False,
                "candidate_state": "sandbox_candidate",
                "truth_effect": "none",
                "certification_claim": "none",
                "controller_truth_modified": False,
                "execution_contract": {"run_tick": False, "simulate": False, "dry_run_only": True},
            },
        }

        page.click("#fault-sandbox-next")
        page.wait_for_url("**/fault-injection-sandbox")
        expect(page.locator("#fault-sandbox-result-state")).to_have_text("配置已生成")
        expect(page.locator("#fault-sandbox-result-summary")).to_contain_text("DOCX L1-L4 模板候选沙盒计划已载入")
        expect(page.locator("#fault-sandbox-source-summary")).to_contain_text("DOCX L1-L4 模板候选已接入故障矩阵")
        expect(page.locator("#fault-sandbox-decision-next-action")).to_contain_text("确认后生成修订单")
        assert page.locator("#fault-sandbox-decision-next-action").evaluate(
            "element => element.scrollWidth <= element.clientWidth + 1"
        ) is True
        expect(page.locator("#fault-sandbox-review-row-count")).to_have_text("7 行")
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint36-row='sandbox-review']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-evidence-trace-rows [data-blueprint36-evidence-row='evidence-chain']")).to_have_count(4)
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint36-report-row='replay-report']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-plan-coverage-list")).to_contain_text("DOCX 模板候选预览")
        expect(page.locator("#fault-sandbox-plan-coverage-list")).not_to_contain_text("ui_template_preview")

        page.click("#fault-sandbox-generate")
        expect(page.locator("#fault-sandbox-result-summary")).to_contain_text("DOCX L1-L4 模板候选沙盒计划已刷新")
        expect(page.locator("#fault-sandbox-review-row-count")).to_have_text("7 行")
        expect(page.locator("#fault-sandbox-decision-next-action")).to_contain_text("确认后生成修订单")
        assert page.locator("#fault-sandbox-decision-next-action").evaluate(
            "element => element.scrollWidth <= element.clientWidth + 1"
        ) is True

        page.click('[data-sandbox-report-action="export"]')
        expect(page.locator("#sandbox-review-package-panel")).to_be_visible()
        expect(page.locator("#sandbox-review-package-review-count")).to_have_text("7 审查行")
        expect(page.locator('#sandbox-review-package-invariants [data-boundary-token="truth_effect:none"]')).to_have_count(1)
        assert model_calls == []
        assert tick_calls == []
    finally:
        page.close()


def test_logic_builder_run_and_parameter_drawer_match_selected_final_31_32(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate("() => localStorage.clear()")
        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        page.click("#logic-load-docx-template")
        expect(page.locator('#logic-canvas[data-view-mode="circuit"]')).to_be_visible()

        page.click('#logic-mode-dock [data-logic-mode="parameters"]')
        drawer = page.locator("#logic-run-parameter-drawer")
        expect(drawer).to_be_visible()
        expect(drawer).to_have_attribute("data-blueprint32-surface", "parameter-drawer-final")
        page.wait_for_function(
            """() => {
              const canvas = document.querySelector("#logic-canvas")?.getBoundingClientRect();
              const drawer = document.querySelector("#logic-run-parameter-drawer")?.getBoundingClientRect();
              const bottom = document.querySelector("#logic-bottom-run-strip")?.getBoundingClientRect();
              return Boolean(canvas && drawer && bottom
                && canvas.bottom <= drawer.top - 4
                && drawer.bottom <= bottom.top - 4);
            }"""
        )
        canvas_box = page.locator("#logic-canvas").bounding_box()
        drawer_box = drawer.bounding_box()
        bottom_strip_box = page.locator("#logic-bottom-run-strip").bounding_box()
        assert canvas_box is not None
        assert drawer_box is not None
        assert bottom_strip_box is not None
        assert canvas_box["y"] + canvas_box["height"] <= drawer_box["y"] - 4
        assert drawer_box["y"] + drawer_box["height"] <= bottom_strip_box["y"] - 4
        drawer_covered_nodes = page.evaluate(
            """() => {
              const drawer = document.querySelector("#logic-run-parameter-drawer")?.getBoundingClientRect();
              if (!drawer) return ["missing-drawer"];
              return Array.from(document.querySelectorAll(".logic-circuit-node"))
                .filter((node) => {
                  const box = node.getBoundingClientRect();
                  if (box.width === 0 || box.height === 0) return false;
                  return drawer.left < box.right
                    && drawer.right > box.left
                    && drawer.top < box.bottom
                    && drawer.bottom > box.top;
                })
                .map((node) => node.dataset.demoNodeId || node.dataset.nodeId || node.textContent.trim());
            }"""
        )
        assert drawer_covered_nodes == []
        expect(page.locator("#logic-drawer-tra-threshold")).to_be_visible()
        expect(drawer.locator('label:has(#logic-drawer-tra-threshold) span')).to_have_text("TRA 门限")
        expect(page.locator("#logic-drawer-tra-threshold-value")).to_have_text("350 ft")
        expect(page.locator("#logic-drawer-vdt-label")).to_contain_text("VDT 地速")
        expect(page.locator("#logic-drawer-run-mode")).to_be_visible()
        expect(page.locator("#logic-drawer-run-mode-dry")).to_have_attribute("aria-pressed", "true")
        expect(page.locator("#logic-drawer-run-mode-real")).to_have_attribute("aria-pressed", "false")
        for control_id in ["logic-drawer-apply", "logic-drawer-reset", "logic-drawer-pin", "logic-bottom-drawer-close"]:
            expect(page.locator(f"#{control_id}")).to_be_visible()

        page.click("#logic-drawer-run-mode-real")
        expect(drawer).to_have_attribute("data-run-mode", "real-value")
        expect(page.locator("#logic-drawer-run-mode-real")).to_have_attribute("aria-pressed", "true")
        page.click("#logic-drawer-pin")
        expect(drawer).to_have_attribute("data-drawer-pinned", "true")
        page.click("#logic-drawer-apply")
        expect(page.locator("#logic-run-verdict")).to_contain_text("参数已应用")

        page.click('#logic-mode-dock [data-logic-mode="run"]')
        expect(drawer).to_have_attribute("data-active-tab", "run")
        expect(drawer).to_have_attribute("data-blueprint31-surface", "run-signal-propagation")
        expect(page.locator("#logic-run-frame")).to_be_visible()
        expect(page.locator("#logic-run-verdict")).to_be_visible()
        expect(page.locator("#logic-run-signals")).to_be_visible()
        page.click('#logic-run-parameter-drawer [data-run-action="run"]')
        expect(page.locator("#logic-run-frame")).to_contain_text("00:03.24")
        expect(page.locator("#logic-run-verdict")).to_contain_text("运行正常")
        expect(page.locator("#logic-run-signals")).to_contain_text("RA 235")
        expect(page.locator("#logic-run-signals")).to_contain_text("TRA 350")
        expect(page.locator("#logic-run-signals")).to_contain_text("VDT 132")

        page.click("#logic-drawer-reset")
        expect(page.locator("#logic-drawer-tra-threshold-value")).to_have_text("350 ft")
        expect(page.locator("#logic-drawer-run-mode-dry")).to_have_attribute("aria-pressed", "true")
        expect(drawer).to_have_attribute("data-run-mode", "dry-run")
    finally:
        page.close()


def test_desktop_four_step_pages_prioritize_primary_decision_surfaces(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 820})
    pages = [
        ("/requirements-intake", "#requirements-preflight-panel", 230, 220),
        ("/logic-builder", "#logic-canvas", 330, 620),
        ("/fault-injection-prepare", "#fault-decision-board", 360, 150),
        ("/fault-injection-sandbox", ".sandbox-review-gate-panel", 620, 380),
    ]
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, fault, sandbox]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(fault));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandbox));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION, _dense_sandbox_plan()],
        )

        for path, primary_selector, max_y, max_height in pages:
            page.goto(f"{demo_server}{path}", wait_until="networkidle")
            if path == "/logic-builder":
                expect(page.locator("#logic-page-system-strip")).to_be_visible()
                _show_logic_builder_workbench(page)
            strip_box = page.locator('[data-command-strip="deepseek-step"]').bounding_box()
            primary_box = page.locator(primary_selector).bounding_box()
            overflow_count = page.evaluate(
                """() => Array.from(document.querySelectorAll("body *")).filter((el) => {
                  const style = window.getComputedStyle(el);
                  return style.display !== "none"
                    && el.scrollWidth > el.clientWidth + 1
                    && style.overflowX !== "hidden";
                }).length"""
            )
            assert strip_box is not None
            assert primary_box is not None
            assert strip_box["height"] <= 118, path
            assert primary_box["y"] <= max_y, path
            assert primary_box["height"] <= max_height, path
            assert overflow_count == 0, path
            assert page.evaluate("() => Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)") <= 820, path
    finally:
        page.close()


def test_desktop_demo_layout_keeps_primary_surfaces_unclipped(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        fault_for_layout = json.loads(json.dumps(FAULT_PREPARATION))
        fault_for_layout["summary_zh"] = "蓝图候选故障矩阵已准备，仅用于 dry-run 沙盒候选。"
        fault_for_layout["boundary_questions"][0]["prompt_zh"] = "确认本次只生成 dry-run 沙盒建议？"
        fault_for_layout["boundary_answers"] = [
            {
                "id": "boundary_dry_run",
                "prompt_zh": "确认本次只生成 dry-run 沙盒建议？",
                "answer_zh": "确认只用于 dry-run 回放演示。",
            }
        ]
        fault_for_layout["fault_scenarios"].append(
            {
                "id": "fault_sw2_drop",
                "label": "SW2 掉线",
                "node_id": "sw2",
                "fault_type": "dropout",
                "severity": "medium",
                "rationale_zh": "SW2 条件缺失会阻断执行链。",
                "expected_effect_zh": "应保持 THR_LOCK 不释放。",
                "observable_signals": ["sw2_valid", "logic2"],
            }
        )
        fault_for_layout["injection_points"].append(
            {
                "id": "inject_sw2",
                "node_id": "sw2",
                "signal_name": "sw2_valid",
                "injection_mode": "dropout",
                "safe_boundary_zh": "仅 dry-run，不写入控制器状态。",
            }
        )
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, fault, sandbox]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(fault));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandbox));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), fault_for_layout, _dense_sandbox_plan()],
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        expect(page.locator("#logic-workflow-detail")).to_be_visible()
        expect(page.locator("#logic-stream-chunks")).to_be_visible()
        assert page.locator("#logic-workflow-detail").evaluate(
            "el => el.scrollHeight <= el.clientHeight + 1"
        )
        assert page.locator("#logic-stream-chunks").evaluate(
            "el => el.scrollHeight <= el.clientHeight + 1"
        )

        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="networkidle")
        process_box = page.locator("#fault-process").bounding_box()
        layout_box = page.locator(".fault-layout").bounding_box()
        action_strip_box = page.locator("#fault-bottom-action-strip").bounding_box()
        matrix_box = page.locator("#fault-candidate-matrix-panel").bounding_box()
        boundary_list_box = page.locator("#fault-boundary-list").bounding_box()
        save_boundary_box = page.locator("#fault-save-boundaries").bounding_box()
        assert process_box is not None
        assert layout_box is not None
        assert action_strip_box is not None
        assert matrix_box is not None
        assert boundary_list_box is not None
        assert save_boundary_box is not None
        assert process_box["height"] <= 56
        assert matrix_box["y"] <= 320
        assert layout_box["y"] + layout_box["height"] <= action_strip_box["y"]
        assert save_boundary_box["y"] < boundary_list_box["y"]
        assert save_boundary_box["y"] + save_boundary_box["height"] <= action_strip_box["y"] - 4
        assert boundary_list_box["height"] >= 48
        assert boundary_list_box["y"] < action_strip_box["y"]
        assert boundary_list_box["y"] + boundary_list_box["height"] <= action_strip_box["y"] - 4
        boundary_items = page.locator("#fault-boundary-list .fault-boundary-item")
        expect(boundary_items).to_have_count(2)
        boundary_item_boxes = boundary_items.evaluate_all(
            """nodes => nodes.map((node) => {
              const rect = node.getBoundingClientRect();
              return {x: rect.x, y: rect.y, width: rect.width, height: rect.height};
            })"""
        )
        assert len(boundary_item_boxes) == 2
        assert abs(boundary_item_boxes[0]["y"] - boundary_item_boxes[1]["y"]) <= 2
        assert boundary_item_boxes[0]["x"] + boundary_item_boxes[0]["width"] <= boundary_item_boxes[1]["x"]
        for box in boundary_item_boxes:
            assert box["width"] >= 420
            assert boundary_list_box["y"] <= box["y"] <= boundary_list_box["y"] + 1
            assert box["y"] + box["height"] <= boundary_list_box["y"] + boundary_list_box["height"] + 1
            assert box["y"] + box["height"] <= action_strip_box["y"] - 4
        assert page.locator("#fault-boundary-list").evaluate(
            "el => el.scrollHeight <= el.clientHeight + 2"
        )
        assert page.locator("#fault-process").evaluate(
            "el => el.scrollHeight <= el.clientHeight + 1"
        )
        expect(page.locator("#fault-candidate-matrix-body [data-raw-fault-type='dropout']")).to_have_text("信号丢失")
        fault_type_texts = page.locator("#fault-candidate-matrix-body .fault-matrix-type").evaluate_all(
            "nodes => nodes.map((node) => node.textContent.trim())"
        )
        assert "dropout" not in fault_type_texts
        expect(page.locator("#fault-candidate-matrix-body [data-raw-matrix-trigger='仅 dry-run，不写入控制器状态。']")).to_have_text(
            "仅空跑，不写入控制器状态。"
        )
        expect(page.locator("#fault-candidate-matrix-body [data-raw-matrix-effect='应保持 THR_LOCK 不释放。']")).to_have_text(
            "应保持油门锁不释放。"
        )
        expect(page.locator("#fault-result-summary")).to_have_text("蓝图候选故障矩阵已准备，仅用于空跑沙盒候选。")
        expect(page.locator("#fault-result-summary")).to_have_attribute(
            "data-raw-summary", "蓝图候选故障矩阵已准备，仅用于 dry-run 沙盒候选。"
        )
        expect(page.locator("#fault-boundary-list .fault-boundary-item").first.locator("strong")).to_have_text(
            "确认本次只生成空跑沙盒建议？"
        )
        expect(page.locator("#fault-boundary-list textarea[data-boundary-id='boundary_dry_run']")).to_have_attribute(
            "data-boundary-prompt", "确认本次只生成 dry-run 沙盒建议？"
        )
        expect(page.locator("#fault-boundary-list textarea[data-boundary-id='boundary_dry_run']")).to_have_attribute(
            "data-boundary-answer-raw", "确认只用于 dry-run 回放演示。"
        )
        expect(page.locator("#fault-boundary-list textarea[data-boundary-id='boundary_dry_run']")).to_have_value(
            "确认只用于空跑回放演示。"
        )
        assert "dry-run" not in page.locator("body").inner_text()
        expect(page.locator("#fault-candidate-details")).to_be_visible()
        expect(page.locator("#fault-injection-point-details")).to_be_visible()

        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="networkidle")
        for selector in ["#fault-sandbox-decision-board", ".sandbox-review-gate-panel"]:
            expect(page.locator(selector)).to_be_visible()
            assert page.locator(selector).evaluate(
                "el => el.scrollHeight <= el.clientHeight + 1"
            )
        expect(page.locator("#fault-sandbox-primary-gates")).to_contain_text("空跑合同")
        expect(page.locator("#fault-sandbox-primary-gates")).to_contain_text("覆盖完整性")
        expect(page.locator("#fault-sandbox-primary-gates")).to_contain_text("例外/风险已读")
    finally:
        page.close()


def test_deepseek_visual_acceptance_script_generates_first_screen_bundle(
    demo_server: str, tmp_path: Path
) -> None:
    artifact_dir = tmp_path / "deepseek-visual-acceptance"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/deepseek_ui_visual_acceptance.py",
            "--base-url",
            demo_server,
            "--artifact-dir",
            str(artifact_dir),
        ],
        cwd=Path(__file__).resolve().parents[2],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    summary_path = artifact_dir / "visual-acceptance-summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["kind"] == "deepseek-ui-visual-acceptance"
    assert summary["ok"] is True
    assert summary["route_count"] == 5
    assert summary["screenshot_count"] == 10
    assert len(list(artifact_dir.glob("*.png"))) == 10

    routes = {entry["route"] for entry in summary["pages"]}
    assert routes == {
        "/requirements-intake",
        "/logic-builder",
        "/fault-injection-prepare",
        "/fault-injection-sandbox",
    }
    route_keys = {entry["route_key"] for entry in summary["pages"]}
    assert route_keys == {
        "requirements-intake",
        "logic-builder",
        "fault-injection-prepare",
        "fault-injection-sandbox-default",
        "fault-injection-sandbox",
    }
    for entry in summary["pages"]:
        assert entry["missing_visible_surfaces"] == [], entry
        assert entry["missing_existing_surfaces"] == [], entry
        assert entry["geometry"]["vertical_scroll_ok"] is True, entry
        assert entry["geometry"]["horizontal_overflow_count"] == 0, entry
        assert entry["screenshot"].endswith(".png")


def test_deepseek_v4_pro_ui_workbench_demo_flow_without_canvas_mainline(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    geometry: list[dict[str, Any]] = []
    try:
        _install_model_routes(page)

        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        geometry.append(_assert_deepseek_page_contract(page, "requirements-intake"))
        expect(page.locator("#requirements-provider")).to_have_value("deepseek")
        page.fill("#requirements-text", "RA 小于 6ft 且 TRA/SW1/SW2/EEC 条件满足时，释放油门锁。")
        page.click("#requirements-analyze")
        expect(page.locator("#result-state")).to_have_text("可进入逻辑链路")
        expect(page.locator("#requirements-logic-handoff")).to_be_visible()
        expect(page.locator("#requirements-logic-handoff")).to_have_attribute("data-handoff-state", "ready")
        expect(page.locator("#requirements-handoff-spine")).to_have_attribute("data-current-stage", "review")
        expect(page.locator('#requirements-handoff-spine [data-handoff-stage="review"]')).to_have_class(re.compile("is-active"))
        expect(page.locator("#requirements-handoff-anchors")).to_contain_text("原文锚点")
        expect(page.locator("#requirements-handoff-logic")).to_contain_text("节点 /")
        expect(page.locator("#requirements-handoff-review")).to_contain_text("逐段高亮")
        expect(page.locator("#logic-builder-next")).to_be_enabled()
        _screenshot(page, "01-requirements-intake-ready")

        page.click("#logic-builder-next")
        page.wait_for_url("**/logic-builder")
        _show_logic_builder_workbench(page)
        expect(page.locator("#logic-trust-source-state")).to_contain_text("需求页交接已接收")
        expect(page.locator("#logic-result-state")).to_have_text("电路图已完成绘制")
        expect(page.locator("#logic-canvas-counts")).to_contain_text("20 个电路节点")
        expect(page.locator("#logic-circuit-eval-panel")).to_be_visible()
        assert page.locator("#logic-circuit-status-details").evaluate("element => element.open") is False
        expect(page.locator("#logic-workbench-drawers")).to_have_attribute("data-active-tab", "none")
        page.select_option("#logic-circuit-preset-select", "max-reverse")
        expect(page.locator("#logic-circuit-status-badge")).to_have_text("已放出")
        expect(page.locator('[data-demo-node-id="thr_lock"]')).to_have_attribute("data-state", "active")
        geometry.append(_assert_deepseek_page_contract(page, "logic-builder"))
        _screenshot(page, "02-logic-builder-drawing")

        page.click("#logic-fault-next")
        page.wait_for_url("**/fault-injection-prepare")
        expect(page.locator("#fault-result-state")).to_have_text("候选已生成")
        expect(page.locator("#fault-scenario-count")).to_have_text("1 场景")
        expect(page.locator("#fault-coverage-evidence")).to_be_hidden()
        expect(page.locator("#fault-coverage-evidence")).to_contain_text("自动补齐证据")
        expect(page.locator("#fault-coverage-evidence")).to_contain_text("thr_lock_rel")
        for index in range(page.locator("textarea[data-boundary-id]").count()):
            page.locator("textarea[data-boundary-id]").nth(index).fill("确认空跑演示边界。")
        expect(page.locator("#fault-sandbox-next")).to_be_enabled()
        fault_boundary_panel_box = page.locator(".fault-boundary-panel").bounding_box()
        fault_boundary_list_box = page.locator("#fault-boundary-list").bounding_box()
        fault_action_strip_box = page.locator("#fault-bottom-action-strip").bounding_box()
        assert fault_boundary_panel_box and fault_boundary_list_box and fault_action_strip_box
        assert fault_boundary_panel_box["height"] >= 350
        assert fault_action_strip_box["y"] - (fault_boundary_panel_box["y"] + fault_boundary_panel_box["height"]) <= 96
        assert page.locator("#fault-boundary-list").evaluate(
            "node => node.scrollHeight <= node.clientHeight + 1"
        ) is True
        fault_boundary_textarea_boxes = page.locator("#fault-boundary-list textarea[data-boundary-id]").evaluate_all(
            """nodes => nodes.map((node) => {
              const rect = node.getBoundingClientRect();
              return {height: rect.height, scrollHeight: node.scrollHeight, clientHeight: node.clientHeight};
            })"""
        )
        assert fault_boundary_textarea_boxes
        assert min(box["height"] for box in fault_boundary_textarea_boxes) >= 230
        assert all(box["scrollHeight"] <= box["clientHeight"] + 1 for box in fault_boundary_textarea_boxes)
        fault_source_defer_box = page.locator("#fault-source-defer").bounding_box()
        assert fault_source_defer_box is not None
        assert fault_source_defer_box["height"] >= 320
        assert fault_action_strip_box["y"] - (fault_source_defer_box["y"] + fault_source_defer_box["height"]) <= 16
        assert page.locator("#fault-source-defer").evaluate("node => node.scrollHeight <= node.clientHeight + 1")
        geometry.append(_assert_deepseek_page_contract(page, "fault-injection-prepare"))
        _screenshot(page, "03-fault-injection-prepare")

        page.click("#fault-sandbox-next")
        page.wait_for_url("**/fault-injection-sandbox")
        expect(page.locator("#fault-sandbox-result-state")).to_have_text("配置已生成")
        expect(page.locator("#fault-sandbox-review-gate")).to_have_text("需确认 3 个一级闸门")
        expect(page.locator("#fault-sandbox-plan-coverage-evidence")).to_be_hidden()
        expect(page.locator("#fault-sandbox-plan-coverage-evidence")).to_contain_text("自动补齐证据")
        expect(page.locator("#fault-sandbox-plan-coverage-evidence")).to_contain_text("auto_fault_thr_lock_rel")
        for index in range(page.locator("input[data-sandbox-confirm]").count()):
            page.locator("input[data-sandbox-confirm]").nth(index).check()
        expect(page.locator("#fault-sandbox-review-gate")).to_have_text("可进入逻辑修订")
        sandbox_inspector_box = page.locator("#fault-sandbox-diagnosis-inspector").bounding_box()
        sandbox_evidence_trace_box = page.locator("#fault-sandbox-evidence-trace").bounding_box()
        assert sandbox_inspector_box and sandbox_evidence_trace_box
        assert sandbox_evidence_trace_box["height"] >= 180
        assert sandbox_evidence_trace_box["y"] + sandbox_evidence_trace_box["height"] <= (
            sandbox_inspector_box["y"] + sandbox_inspector_box["height"] + 1
        )
        expect(page.locator("#fault-sandbox-evidence-trace .sandbox-evidence-trace-row:visible")).to_have_count(4)
        assert page.locator("#fault-sandbox-evidence-trace").evaluate(
            "node => node.scrollHeight <= node.clientHeight + 1"
        ) is True
        geometry.append(_assert_deepseek_page_contract(page, "fault-injection-sandbox"))
        _screenshot(page, "04-fault-injection-sandbox")

        page.click("#fault-sandbox-revision-next")
        page.wait_for_url("**/logic-builder")
        _show_logic_builder_workbench(page)
        expect(page.locator("#logic-workbench-drawers")).to_have_attribute("data-active-tab", "change")
        expect(page.locator('#logic-workbench-drawers [data-workbench-tab="change"]')).to_have_attribute(
            "aria-selected",
            "true",
        )
        expect(page.locator("#logic-revision-handoff")).to_be_visible()
        expect(page.locator("#logic-revision-handoff-title")).to_have_text("来自沙盒审查")
        geometry.append(_assert_deepseek_page_contract(page, "logic-builder"))
        _screenshot(page, "05-logic-builder-revision-handoff")
    finally:
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        (ARTIFACT_DIR / "geometry-evidence.json").write_text(
            json.dumps(geometry, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        page.close()


def test_deepseek_ui_reports_live_key_and_submits_live_only_request(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 840})
    captured_requests: list[dict[str, Any]] = []
    try:
        page.route(
            "**/api/requirements-intake/provider-status?provider=deepseek",
            lambda route: _fulfill_json(
                route,
                {
                    "provider": "deepseek",
                    "model": "deepseek-v4-pro",
                    "api_base": "https://api.deepseek.com",
                    "key_available": True,
                    "key_source": "env:DEEPSEEK_API_KEY",
                    "live_ready": True,
                },
            ),
        )

        def capture_analyze(route: Any) -> None:
            captured_requests.append(json.loads(route.request.post_data or "{}"))
            _fulfill_json(route, REQUIREMENTS_READY)

        page.route("**/api/requirements-intake/analyze", capture_analyze)
        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        expect(page.locator("#requirements-provider-status")).to_contain_text("DeepSeek 已接入")
        expect(page.locator("#requirements-provider-key-source")).to_contain_text("env:DEEPSEEK_API_KEY")
        expect(page.locator("#requirements-live-only")).to_be_checked()

        page.fill("#requirements-text", "RA 小于 6ft 且 TRA/SW1/SW2/EEC 条件满足时，释放油门锁。")
        page.click("#requirements-analyze")
        expect(page.locator("#result-state")).to_have_text("可进入逻辑链路")
    finally:
        page.close()

    assert captured_requests
    assert captured_requests[0]["provider"] == "deepseek"
    assert captured_requests[0]["allow_fallback"] is False


def test_requirements_intake_renders_local_preparse_before_deepseek_enhancement(
    demo_server: str,
    browser: Any,
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    calls: list[str] = []
    pending_deepseek_routes: list[Any] = []
    local_payload = {
        **REQUIREMENTS_READY,
        "summary_zh": "本地预解析已先产出 L1-L4 结构。",
        "llm": {"provider": "local-preparse", "response_source": "deterministic_preparse"},
        "deterministic_preparse": {
            "available": True,
            "applied": True,
            "reason": "local_preparse_first",
        },
        "concept_logic_nodes": [{"id": f"local_{index}", "label": f"L{index}", "node_kind": "logic"} for index in range(1, 14)],
        "concept_edges": [{"source": f"local_{index}", "target": f"local_{index + 1}", "label": "local"} for index in range(1, 13)],
    }
    deepseek_payload = {
        **REQUIREMENTS_READY,
        "summary_zh": "DeepSeek 增强结果已刷新。",
        "concept_logic_nodes": REQUIREMENTS_READY["concept_logic_nodes"] + [
            {"id": "deepseek_extra", "label": "VDT", "node_kind": "component"},
        ],
    }
    try:
        page.route("**/api/requirements-intake/provider-status?provider=deepseek", lambda route: _fulfill_json(route, {
            "provider": "deepseek",
            "model": "deepseek-v4-pro",
            "api_base": "https://api.deepseek.com",
            "key_available": True,
            "key_source": "env:DEEPSEEK_API_KEY",
            "live_ready": True,
        }))

        def fulfill_local(route: Any) -> None:
            calls.append("local")
            _fulfill_json(route, local_payload)

        def fulfill_deepseek(route: Any) -> None:
            calls.append("deepseek")
            pending_deepseek_routes.append(route)

        page.route("**/api/requirements-intake/local-preparse", fulfill_local)
        page.route("**/api/requirements-intake/analyze", fulfill_deepseek)

        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        stream = page.locator("#requirements-generation-stream")
        expect(stream).to_be_attached()
        expect(stream.locator("[data-stream-step]")).to_have_count(4)
        expect(stream.locator("[data-stream-step='read']")).to_have_attribute("data-state", "idle")

        page.fill("#requirements-text", "RA 小于 6ft，SW1/SW2 有效，TRA 进入反推区，VDT 90%。")
        page.click("#requirements-analyze")
        expect(stream).to_be_visible()

        expect(page.locator("#requirements-status")).to_have_text("本地预解析已就绪")
        expect(page.locator("#requirements-summary")).to_have_text("本地预解析已先产出 L1-L4 结构。")
        expect(page.locator("#graph-counts")).to_have_text("13 nodes · 12 edges")
        expect(stream.locator("[data-stream-step='read']")).to_have_attribute("data-state", "complete")
        expect(stream.locator("[data-stream-step='parse']")).to_have_attribute("data-state", "complete")
        expect(stream.locator("[data-stream-step='send']")).to_have_attribute("data-state", "active")
        expect(page.locator("#process-title")).to_have_text("本地预解析已就绪")

        assert pending_deepseek_routes
        _fulfill_json(pending_deepseek_routes.pop(0), deepseek_payload)
        expect(page.locator("#requirements-summary")).to_have_text("DeepSeek 增强结果已刷新。")
        expect(page.locator("#requirements-status")).to_have_text("完成")
        expect(stream.locator("[data-stream-step='render']")).to_have_attribute("data-state", "complete")
        expect(page.locator("#process-title")).to_have_text("分析完成")
    finally:
        page.close()

    assert calls == ["local", "deepseek"]


def test_requirements_intake_missing_key_uses_local_preparse_without_live_call(
    demo_server: str,
    browser: Any,
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    calls: list[str] = []
    local_payload = {
        **REQUIREMENTS_READY,
        "summary_zh": "本地预解析已生成可继续的 L1-L4 候选。",
        "llm": {"provider": "local-preparse", "response_source": "deterministic_preparse"},
        "deterministic_preparse": {"available": True, "applied": True, "reason": "local_preparse_first"},
        "concept_logic_nodes": [{"id": f"local_{index}", "label": f"L{index}", "node_kind": "logic"} for index in range(1, 14)],
        "concept_edges": [{"source": f"local_{index}", "target": f"local_{index + 1}", "label": "local"} for index in range(1, 13)],
    }
    try:
        page.route("**/api/requirements-intake/provider-status?provider=deepseek", lambda route: _fulfill_json(route, {
            "provider": "deepseek",
            "model": "deepseek-v4-pro",
            "api_base": "https://api.deepseek.com",
            "key_available": False,
            "key_source": "",
            "live_ready": False,
            "checked": ["DEEPSEEK_API_KEY"],
        }))

        def fulfill_local(route: Any) -> None:
            calls.append("local")
            _fulfill_json(route, local_payload)

        def reject_live(route: Any) -> None:
            calls.append("deepseek")
            route.fulfill(status=503, content_type="application/json", body='{"error":"missing_api_key"}')

        page.route("**/api/requirements-intake/local-preparse", fulfill_local)
        page.route("**/api/requirements-intake/analyze", reject_live)

        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        expect(page.locator("#requirements-preflight-panel")).to_be_visible()
        expect(page.locator("#requirements-preflight-live-state")).to_have_text("未接入")
        expect(page.locator("#requirements-analyze")).to_have_text("检查：本地预解析")
        page.fill("#requirements-text", "RA 小于 6ft，SW1/SW2 有效，TRA 进入反推区，VDT 90%。")
        page.click("#requirements-analyze")

        expect(page.locator("#requirements-status")).to_have_text("本地候选可继续")
        expect(page.locator("#result-state")).to_have_text("可进入逻辑链路")
        expect(page.locator("#requirements-summary")).to_have_text("本地预解析已生成可继续的 L1-L4 候选。")
        expect(page.locator("#graph-counts")).to_have_text("13 nodes · 12 edges")
        expect(page.locator("#logic-builder-next")).to_be_enabled()
    finally:
        page.close()

    assert calls == ["local"]


def test_requirements_intake_preserves_local_candidate_when_deepseek_enhancement_fails(
    demo_server: str,
    browser: Any,
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    local_payload = {
        **REQUIREMENTS_READY,
        "summary_zh": "本地预解析已先产出 L1-L4 结构。",
        "llm": {"provider": "local-preparse", "response_source": "deterministic_preparse"},
        "deterministic_preparse": {"available": True, "applied": True, "reason": "local_preparse_first"},
        "concept_logic_nodes": [{"id": f"local_{index}", "label": f"L{index}", "node_kind": "logic"} for index in range(1, 14)],
        "concept_edges": [{"source": f"local_{index}", "target": f"local_{index + 1}", "label": "local"} for index in range(1, 13)],
    }
    try:
        page.route("**/api/requirements-intake/provider-status?provider=deepseek", lambda route: _fulfill_json(route, {
            "provider": "deepseek",
            "model": "deepseek-v4-pro",
            "api_base": "https://api.deepseek.com",
            "key_available": True,
            "key_source": "env:DEEPSEEK_API_KEY",
            "live_ready": True,
        }))
        page.route("**/api/requirements-intake/local-preparse", lambda route: _fulfill_json(route, local_payload))
        page.route(
            "**/api/requirements-intake/analyze",
            lambda route: route.fulfill(
                status=503,
                content_type="application/json",
                body='{"error":"missing_api_key"}',
            ),
        )

        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        page.fill("#requirements-text", "RA 小于 6ft，SW1/SW2 有效，TRA 进入反推区，VDT 90%。")
        page.click("#requirements-analyze")

        expect(page.locator("#requirements-status")).to_have_text("DeepSeek 增强失败")
        expect(page.locator("#result-state")).to_have_text("可进入逻辑链路")
        expect(page.locator("#process-title")).to_have_text("DeepSeek 增强失败，可稍后重试")
        expect(page.locator("#requirements-summary")).to_have_text("本地预解析已先产出 L1-L4 结构。")
        expect(page.locator("#graph-counts")).to_have_text("13 nodes · 12 edges")
        expect(page.locator("#logic-builder-next")).to_be_enabled()
    finally:
        page.close()


def test_requirements_intake_preflight_imports_replay_and_hydrates_draft(
    demo_server: str,
    browser: Any,
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    model_calls: list[str] = []
    try:
        page.route("**/api/requirements-intake/deepseek-live-demo-replay", lambda route: _fulfill_json(route, _replay_payload()))

        def reject_model_call(route: Any) -> None:
            model_calls.append(route.request.url)
            route.fulfill(status=500, content_type="application/json", body='{"error":"model_call_forbidden"}')

        page.route("**/api/requirements-intake/analyze", reject_model_call)
        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        expect(page.locator("#requirements-replay-import")).to_be_visible()
        page.click("#requirements-replay-import")

        expect(page.locator("#requirements-status")).to_have_text("回放已导入")
        expect(page.locator("#result-state")).to_have_text("可进入逻辑链路")
        expect(page.locator("#graph-counts")).to_have_text("3 nodes · 2 edges")
        expect(page.locator("#logic-builder-next")).to_be_enabled()

        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        expect(page.locator("#requirements-status")).to_have_text("已恢复回放草稿")
        expect(page.locator("#result-state")).to_have_text("可进入逻辑链路")
        expect(page.locator("#graph-counts")).to_have_text("3 nodes · 2 edges")
        assert model_calls == []
    finally:
        page.close()


def test_logic_builder_circuit_view_uses_demo_snapshot_presets(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        expect(page.locator("#logic-circuit-eval-panel")).to_be_visible()
        expect(page.locator("#logic-canvas-counts")).to_contain_text("20 个电路节点")
        assert page.locator("#logic-circuit-status-details").evaluate("element => element.open") is False
        expect(page.locator("#logic-workbench-drawers")).to_have_attribute("data-active-tab", "none")

        page.select_option("#logic-circuit-preset-select", "max-reverse")
        expect(page.locator("#logic-circuit-preset-status")).to_contain_text("最大反推")
        expect(page.locator("#logic-circuit-status-badge")).to_have_text("已放出")
        expect(page.locator("#logic-circuit-status-summary")).to_have_text("L4 满足，油门锁释放。油门反向段解锁。")
        expect(page.locator("#logic-circuit-hud-sw1")).to_have_text("闭合")
        expect(page.locator("#logic-circuit-hud-sw2")).to_have_text("闭合")
        expect(page.locator("#logic-circuit-hud-tls")).to_have_text("已解锁")
        expect(page.locator("#logic-circuit-hud-vdt90")).to_have_text("≥90%")
        expect(page.locator("#logic-circuit-hud-logic")).to_contain_text("L4:通")
        expect(page.locator("#logic-circuit-hud-thr-lock")).to_have_text("已释放")
        expect(page.locator('[data-demo-node-id="thr_lock"]')).to_have_attribute("data-state", "active")
        expect(page.locator('.logic-circuit-wire[data-source="logic4"][data-target="thr_lock"]')).to_have_attribute(
            "data-state",
            "active",
        )

        page.select_option("#logic-circuit-preset-select", "inhibit-block")
        expect(page.locator("#logic-circuit-status-badge")).to_have_text("异常")
        expect(page.locator("#logic-circuit-status-summary")).to_have_text("反推被抑制：抑制信号为真，展开链路阻塞。")
        expect(page.locator("#logic-circuit-hud-vdt90")).to_have_text("待到位")
        expect(page.locator("#logic-circuit-hud-thr-lock")).to_have_text("已阻断")
        expect(page.locator('.logic-circuit-wire[data-source="reverser_inhibited"][data-target="logic1"]')).to_have_attribute(
            "data-state",
            "fault",
        )
    finally:
        page.close()


def test_logic_builder_shows_demo_reconstruction_mode_and_concept_mode_warning(
    demo_server: str,
    browser: Any,
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        expect(page.locator("#logic-reconstruction-mode-panel")).to_be_visible()
        expect(page.locator("#logic-reconstruction-mode")).to_have_text("当前模式：演示舱一致电路图")
        expect(page.locator("#logic-reconstruction-fidelity")).to_have_text("链路覆盖：20/20 节点 · 23/23 连线")
        expect(page.locator("#logic-demo-bridge")).to_have_text("打开对齐视图")
        expect(page.locator("#logic-demo-bridge")).to_have_attribute("href", "/demo-reconstruction")
        assert page.locator("#logic-demo-bridge").get_attribute("data-primary-next-action") is None

        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            LOGIC_DRAWING,
        )
        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        expect(page.locator("#logic-reconstruction-mode")).to_have_text("当前模式：概念图，尚未对齐演示舱电路")
        expect(page.locator("#logic-reconstruction-fidelity")).to_have_text("链路覆盖：未启用")
        expect(page.locator("#logic-demo-bridge")).to_have_text("打开对照视图")
        expect(page.locator("#logic-canvas-counts")).to_have_text("3 个节点 · 2 条连线 · 1 个面板")
    finally:
        page.close()


def test_demo_reconstruction_comparison_page_shows_original_and_current_replica(
    demo_server: str,
    browser: Any,
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        page.click("#logic-demo-bridge")
        page.wait_for_url("**/demo-reconstruction")
        page.wait_for_load_state("networkidle")

        expect(page.locator("#demo-reconstruction-console-frame")).to_be_visible()
        expect(page.locator("#demo-reconstruction-browser-evidence")).to_be_visible()
        expect(page.locator("#demo-reconstruction-docx-circuit-map summary")).to_be_visible()
        expect(page.locator("#demo-reconstruction-mode")).to_have_text("当前模式：原始反推需求 DOCX 到 demo.html 完整电路")
        expect(page.locator("#demo-reconstruction-fidelity")).to_have_text("复刻度：20/20 节点 · 23/23 连线")
        expect(page.locator("#demo-reconstruction-browser-evidence")).to_contain_text("节点")
        expect(page.locator("#demo-reconstruction-browser-evidence")).to_contain_text("连线")
        expect(page.locator("#demo-reconstruction-browser-evidence")).to_contain_text("预设场景")
        expect(page.locator("#demo-reconstruction-browser-evidence")).to_contain_text("状态输出")
        expect(page.locator("#demo-reconstruction-preset-list")).to_contain_text("着陆展开")
        expect(page.locator("#demo-reconstruction-status-list")).to_contain_text("THR_LOCK")
        expect(page.locator("#demo-reconstruction-node-list li")).to_have_count(20)
        expect(page.locator("#demo-reconstruction-wire-list li")).to_have_count(23)

        console_box = page.locator("#demo-reconstruction-console-frame").bounding_box()
        evidence_box = page.locator("#demo-reconstruction-browser-evidence").bounding_box()
        source_box = page.locator("#demo-reconstruction-docx-circuit-map").bounding_box()
        assert console_box is not None and evidence_box is not None
        assert source_box is not None
        assert console_box["width"] > 360
        assert evidence_box["width"] >= 360
        assert page.locator("#demo-reconstruction-docx-circuit-map").evaluate("element => element.open") is False
        assert console_box["y"] < source_box["y"]
    finally:
        page.close()


def test_deepseek_workflow_streams_chunks_before_model_final_response(
    demo_server: str,
    browser: Any,
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    try:
        logic_routes: list[Any] = []
        page.route("**/api/requirements-intake/draw-logic", lambda route: logic_routes.append(route))
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(requirements) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.removeItem("ai-fantui-logic-builder-drawing-v1");
              localStorage.removeItem("ai-fantui-fault-injection-preparation-v1");
              localStorage.removeItem("ai-fantui-fault-injection-sandbox-plan-v1");
            }""",
            REQUIREMENTS_READY,
        )
        page.goto(f"{demo_server}/logic-builder", wait_until="domcontentloaded")
        expect(page.locator("#logic-stream-chunks")).to_be_visible()
        _show_logic_builder_workbench(page)
        expect(page.locator("#logic-stream-chunks")).to_be_visible()
        expect(page.locator('#logic-stream-chunks [data-stream-chunk="load"]')).to_contain_text("已读取需求")
        expect(page.locator('#logic-stream-chunks [data-stream-chunk="model"]')).to_contain_text("正在生成图纸")
        expect(page.locator("#logic-step-model")).to_have_attribute("data-state", "active")
        assert logic_routes
        _fulfill_json(logic_routes.pop(0), _circuit_view_drawing())
        expect(page.locator('#logic-stream-chunks [data-stream-chunk="render"]')).to_contain_text("渲染电路")

        fault_routes: list[Any] = []
        page.route("**/api/requirements-intake/prepare-fault-injection", lambda route: fault_routes.append(route))
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-fault-injection-preparation-v1");
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing()],
        )
        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="domcontentloaded")
        expect(page.locator('#fault-stream-chunks [data-stream-chunk="load"]')).to_contain_text("已读取图纸")
        expect(page.locator('#fault-stream-chunks [data-stream-chunk="model"]')).to_contain_text("DeepSeek 正在准备")
        expect(page.locator("#fault-step-model")).to_have_attribute("data-state", "active")
        assert fault_routes
        _fulfill_json(fault_routes.pop(0), FAULT_PREPARATION)
        expect(page.locator('#fault-stream-chunks [data-stream-chunk="boundary"]')).to_contain_text("边界确认")

        sandbox_routes: list[Any] = []
        page.route("**/api/requirements-intake/prepare-fault-injection/sandbox", lambda route: sandbox_routes.append(route))
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(faultPayload) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.removeItem("ai-fantui-fault-injection-sandbox-plan-v1");
            }""",
            FAULT_PREPARATION,
        )
        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="domcontentloaded")
        expect(page.locator('#sandbox-stream-chunks [data-stream-chunk="load"]')).to_contain_text("已读取准备")
        expect(page.locator('#sandbox-stream-chunks [data-stream-chunk="model"]')).to_contain_text("DeepSeek 正在配置")
        expect(page.locator("#fault-sandbox-step-model")).to_have_attribute("data-state", "active")
        assert sandbox_routes
        _fulfill_json(sandbox_routes.pop(0), SANDBOX_PLAN)
        expect(page.locator('#sandbox-stream-chunks [data-stream-chunk="review"]')).to_contain_text("审查清单")
    finally:
        page.close()


def test_logic_builder_circuit_inputs_default_to_compact_details(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 900, "height": 760})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        page.click('#logic-collapsed-tool-rail [data-panel-toggle="left"]')
        expect(page.locator("main.logic-shell")).to_have_attribute("data-left-rail-state", "expanded")
        expect(page.locator("#logic-circuit-eval-panel")).to_be_visible()
        expect(page.locator("#logic-circuit-status-badge")).to_be_visible()
        expect(page.locator("#logic-circuit-preset-select")).to_be_visible()
        expect(page.locator('#logic-circuit-preset-select option[value="max-reverse"]')).to_have_text("最大反推")
        expect(page.locator("button[data-circuit-preset]")).to_have_count(0)
        assert page.locator("#logic-circuit-input-details").evaluate("element => element.open") is False
        expect(page.locator("#logic-circuit-tra")).to_be_hidden()
        expect(page.locator("#logic-circuit-engine-running")).to_be_hidden()
        expect(page.locator("#logic-circuit-status-details")).to_be_hidden()

        page.select_option("#logic-circuit-preset-select", "max-reverse")
        expect(page.locator("#logic-circuit-status-badge")).to_have_text("已放出")
        assert page.locator("#logic-circuit-input-details").evaluate("element => element.open") is False

        page.click("#logic-circuit-input-details > summary")
        expect(page.locator("#logic-circuit-tra")).to_be_visible()
        expect(page.locator("#logic-circuit-engine-running")).to_be_visible()
        expect(page.locator("#logic-circuit-status-details")).to_be_visible()
        page.locator("#logic-circuit-tra").evaluate(
            """(input) => {
              input.value = "-15";
              input.dispatchEvent(new Event("input", {bubbles: true}));
              input.dispatchEvent(new Event("change", {bubbles: true}));
            }"""
        )
        expect(page.locator("#logic-circuit-tra-value")).to_have_text("-15.0°")
    finally:
        page.close()


def test_logic_builder_left_rail_merges_source_status_and_trust_counts(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 900, "height": 760})
    drawing = _circuit_view_drawing()
    for node in drawing["circuit_view"]["nodes"]:
        if node["id"] == "radio_altitude_ft":
            node["source_anchors"] = [{"id": "B81", "kind": "正文条件", "quote_zh": "飞机离地小于6ft时"}]
            break
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            drawing,
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        expect(page.locator("#logic-engineering-rail")).to_be_visible()
        expect(page.locator("#logic-engineering-rail #logic-status-rail")).to_be_visible()
        expect(page.locator("#logic-engineering-rail #logic-circuit-eval-panel")).to_be_visible()
        expect(page.locator("#logic-status-rail [data-status-rail-section]")).to_have_count(3)
        expect(page.locator('#logic-status-rail [data-status-rail-section="trust"]')).to_be_visible()
        expect(page.locator('#logic-status-rail [data-status-rail-section="source"]')).to_be_hidden()
        expect(page.locator('#logic-status-rail [data-status-rail-section="drawing"]')).to_be_hidden()
        expect(page.locator("#logic-rail-detail-details")).to_be_visible()
        assert page.locator("#logic-rail-detail-details").evaluate("element => element.open") is False
        expect(page.locator("#logic-status-source-count")).to_have_text("1")
        expect(page.locator("#logic-status-local-count")).to_have_text("19")
        expect(page.locator("#logic-status-assumption-count")).to_have_text("0")
        expect(page.locator("#logic-source-trust-summary")).to_have_text("来源覆盖已确认")
        expect(page.locator("#logic-circuit-core-inputs")).to_be_visible()
        expect(page.locator("#logic-circuit-core-inputs [data-core-input]")).to_have_count(4)
        expect(page.locator('[data-core-input="tra"]')).to_contain_text("TRA")
        expect(page.locator('[data-core-input="ra"]')).to_contain_text("RA")
        expect(page.locator('[data-core-input="n1k"]')).to_contain_text("N1K")
        expect(page.locator('[data-core-input="vdt"]')).to_contain_text("VDT")
        expect(page.locator("#logic-circuit-preset-menu")).to_be_visible()
        expect(page.locator('label[for="logic-circuit-preset-select"]')).to_have_text("场景预设")
        expect(page.locator("#logic-circuit-preset-select")).to_be_visible()
        expect(page.locator("button[data-circuit-preset]")).to_have_count(0)
        expect(page.locator("#logic-circuit-input-details")).to_be_visible()
        assert page.locator("#logic-circuit-input-details").evaluate("element => element.open") is False
        expect(page.locator("#logic-circuit-tra")).to_be_hidden()

        direct_panels = page.eval_on_selector_all(
            "aside.logic-inspector > section.logic-panel",
            """(panels) => panels.map((panel) => ({
              id: panel.id || "",
              text: panel.innerText,
            }))""",
        )
        assert [panel["id"] for panel in direct_panels] == ["logic-engineering-rail"]
        direct_kickers = page.eval_on_selector_all(
            "aside.logic-inspector > section.logic-panel > .logic-kicker",
            "(kickers) => kickers.map((kicker) => kicker.textContent.trim())",
        )
        assert direct_kickers == ["状态与输入"]
        for old_kicker in ("ENGINEERING RAIL", "INPUT", "MODEL OUTPUT", "READING LOAD"):
            assert old_kicker not in direct_kickers

        rail_box = page.locator("#logic-engineering-rail").bounding_box()
        assert rail_box is not None
        assert rail_box["height"] <= 455
    finally:
        page.close()


def test_logic_builder_detail_area_defaults_to_three_decision_cards(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1200, "height": 820})
    drawing = _circuit_view_drawing()
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            drawing,
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        board = page.locator('[data-decision-board="logic-details"]')
        expect(board).to_be_hidden()
        expect(board.locator(".logic-detail-card")).to_have_count(3)
        expect(board.locator('[data-detail-card="selection"] h2')).to_have_text("当前选择")
        expect(board.locator('[data-detail-card="source"] h2')).to_have_text("来源判断")
        expect(board.locator('[data-detail-card="next"] h2')).to_have_text("下一步")
        expect(board.locator("#logic-detail-selected-node")).to_have_text("未选择")
        expect(board.locator("#logic-detail-source-summary")).to_have_text("来源覆盖已确认")
        expect(board.locator("#logic-detail-next-action")).to_contain_text("油门锁")
        expect(page.locator("#logic-workbench-drawers")).to_have_attribute("data-active-tab", "none")
        expect(page.locator("#logic-drawing-notes-details")).to_be_hidden()
        expect(page.locator("#logic-change-loop-details")).to_be_hidden()
        expect(page.locator("#logic-change-history-details")).to_be_hidden()

        page.click('[data-demo-node-id="sw1"]')
        expect(board.locator("#logic-detail-selected-node")).to_have_text("sw1")
        expect(page.locator("#logic-workbench-drawers")).to_have_attribute("data-active-tab", "none")
        expect(page.locator("#logic-annotation-popover")).to_be_visible()
        expect(page.locator("#logic-selected-target-label")).to_contain_text("sw1")
    finally:
        page.close()


def test_logic_builder_page_reframes_around_circuit_workbench_shell(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 960})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        expect(page.locator("#logic-page-system-strip")).to_be_visible()
        _show_logic_builder_workbench(page)
        expect(page.locator("main.logic-shell")).to_have_attribute("data-workstation-shell", "canvas-first")
        expect(page.locator("main.logic-shell")).to_have_attribute("data-workstation-state", "primary")
        expect(page.locator("main.logic-shell")).to_have_attribute("data-blueprint27-rhythm", "compact-canvas")
        expect(page.locator("main.logic-shell")).to_have_attribute("data-unified-inspector-state", "none")
        expect(page.locator("#logic-page-system-strip")).to_be_visible()
        expect(page.locator("#logic-page-system-strip")).to_have_class(re.compile(r"logic-command-strip"))
        expect(page.locator("#logic-page-system-strip")).to_have_attribute(
            "data-blueprint27-compact-topbar", "step-progress-workflow"
        )
        expect(page.locator("#logic-page-system-strip")).to_have_attribute("data-blueprint27-rhythm", "compact-topband")
        expect(page.locator(".logic-topbar")).to_have_count(0)
        strip_box = page.locator("#logic-page-system-strip").bounding_box()
        main_box = page.locator("main.logic-shell").bounding_box()
        canvas_box = page.locator("#logic-canvas").bounding_box()
        assert strip_box is not None
        assert main_box is not None
        assert canvas_box is not None
        assert strip_box["height"] <= 84
        assert strip_box["y"] + strip_box["height"] - main_box["y"] <= 104
        expect(page.locator("#logic-page-system-strip .logic-command-title h1")).to_have_text("逻辑复制")
        expect(page.locator("#logic-page-system-strip #logic-process")).to_be_visible()
        expect(page.locator("#logic-page-system-strip #logic-workflow-overview")).to_be_visible()
        expect(page.locator("#logic-page-system-strip .logic-controls")).to_be_visible()
        expect(page.locator("#logic-page-system-strip #logic-provider")).to_be_visible()
        expect(page.locator("#logic-page-system-strip #logic-regenerate")).to_be_visible()
        expect(page.locator("#logic-page-system-strip #logic-fault-next")).to_be_visible()
        expect(page.locator("#logic-regenerate")).to_have_text("检查：重新绘制")
        expect(page.locator("#logic-fault-next")).to_have_text("下一步：进入故障准备")
        expect(page.locator("#logic-back")).to_have_text("更多：返回需求")
        expect(page.locator("#logic-canvas-compact-toolbar")).to_be_visible()
        expect(page.locator("#logic-canvas-compact-toolbar")).to_have_class(re.compile(r"logic-canvas-compact-toolbar"))
        expect(page.locator("#logic-canvas-compact-toolbar #logic-canvas-counts")).to_contain_text("20 个电路节点")
        expect(page.locator("#logic-canvas-compact-toolbar #logic-provenance-filter")).to_be_visible()
        expect(page.locator("#logic-canvas-compact-toolbar #logic-canvas-source")).to_be_visible()
        expect(page.locator("#logic-mode-dock [data-logic-mode]")).to_have_count(5)
        expect(page.locator("#logic-mode-dock button")).to_have_count(5)
        expect(page.locator("#logic-mode-dock #logic-command-palette-open")).to_have_count(0)
        expect(page.locator("#logic-command-palette-open")).to_be_visible()
        expect(page.locator("#logic-command-palette-open")).to_have_attribute(
            "data-blueprint-advanced-entry", "command-palette"
        )
        expect(page.locator('.logic-canvas-wrap[data-workstation-stage="primary-canvas"]')).to_be_visible()
        expect(page.locator('.logic-canvas-wrap[data-blueprint29-rhythm="primary-canvas-stage"]')).to_be_visible()
        expect(page.locator('#logic-canvas[data-workstation-canvas="logic-drawing"]')).to_be_visible()
        expect(page.locator('#logic-mode-dock[data-workstation-surface="default-mode-dock"][data-blueprint27-rhythm="five-entry-dock"]')).to_be_visible()
        expect(page.locator('#logic-right-inspector-rail[data-blueprint38-rhythm="collapsed-inspector-rail"]')).to_be_visible()
        expect(page.locator('#logic-bottom-run-strip[data-blueprint38-rhythm="bottom-run-strip"]')).to_be_visible()
        expect(page.locator("#logic-canvas")).to_be_visible()
        _assert_logic_circuit_blueprint_geometry(page)

        strip_box = page.locator("#logic-page-system-strip").bounding_box()
        process_box = page.locator("#logic-process").bounding_box()
        workflow_box = page.locator("#logic-workflow-overview").bounding_box()
        controls_box = page.locator("#logic-page-system-strip .logic-controls").bounding_box()
        toolbar_box = page.locator("#logic-canvas-compact-toolbar").bounding_box()
        provenance_box = page.locator("#logic-provenance-filter").bounding_box()
        source_box = page.locator("#logic-canvas-source").bounding_box()
        canvas_wrap_box = page.locator(".logic-canvas-wrap").bounding_box()
        canvas_box = page.locator("#logic-canvas").bounding_box()
        rail_box = page.locator("#logic-engineering-rail").bounding_box()
        bottom_strip_box = page.locator("#logic-bottom-run-strip").bounding_box()
        assert strip_box is not None
        assert process_box is not None
        assert workflow_box is not None
        assert controls_box is not None
        assert toolbar_box is not None
        assert provenance_box is not None
        assert source_box is not None
        assert canvas_wrap_box is not None
        assert canvas_box is not None
        assert rail_box is not None
        assert bottom_strip_box is not None
        circuit_box = page.locator("#logic-circuit-svg").bounding_box()
        assert circuit_box is not None
        mode_panel_box = page.locator("#logic-reconstruction-mode-panel").bounding_box()
        assert mode_panel_box is not None
        fit_scale = float(page.locator("#logic-canvas").get_attribute("data-fit-scale") or "0")
        fit_offset_x = float(page.locator("#logic-canvas").get_attribute("data-fit-offset-x") or "0")
        left_canvas_gap = circuit_box["x"] - canvas_box["x"]
        right_canvas_gap = (canvas_box["x"] + canvas_box["width"]) - (circuit_box["x"] + circuit_box["width"])
        assert 1.10 <= fit_scale <= 1.15
        assert fit_offset_x >= 0
        assert left_canvas_gap <= 24
        assert right_canvas_gap >= 64
        assert circuit_box["width"] >= 1000
        assert circuit_box["height"] >= 440
        circuit_graph_box = page.locator("#logic-canvas").evaluate(
            """() => {
              const canvas = document.querySelector("#logic-canvas")?.getBoundingClientRect();
              const rail = document.querySelector("#logic-right-inspector-rail")?.getBoundingClientRect();
              const boxes = Array.from(document.querySelectorAll(
                "#logic-canvas .logic-circuit-node, #logic-canvas .logic-circuit-gate, #logic-canvas .logic-output-node"
              )).map((node) => node.getBoundingClientRect()).filter((box) => box.width && box.height);
              if (!canvas || !rail || !boxes.length) return null;
              const graph = {
                top: Math.min(...boxes.map((box) => box.top)),
                bottom: Math.max(...boxes.map((box) => box.bottom)),
                left: Math.min(...boxes.map((box) => box.left)),
                right: Math.max(...boxes.map((box) => box.right)),
              };
              return {
                bottomGap: canvas.bottom - graph.bottom,
                rightRailGap: rail.left - graph.right,
              };
            }"""
        )
        assert circuit_graph_box is not None
        assert circuit_graph_box["bottomGap"] <= 260
        assert circuit_graph_box["rightRailGap"] >= 48
        assert page.evaluate(
            """() => {
              const panel = document.querySelector("#logic-reconstruction-mode-panel")?.getBoundingClientRect();
              const labels = Array.from(document.querySelectorAll("#logic-circuit-svg .logic-circuit-column-label"))
                .map((label) => label.getBoundingClientRect());
              return Boolean(panel) && labels.every((label) => (
                panel.right < label.left || panel.left > label.right || panel.bottom < label.top || panel.top > label.bottom
              ));
            }"""
        ) is True
        assert circuit_box["y"] + circuit_box["height"] < bottom_strip_box["y"]
        assert mode_panel_box["y"] + mode_panel_box["height"] < bottom_strip_box["y"] - 6
        assert strip_box["height"] <= 84
        assert process_box["height"] <= 82
        assert workflow_box["height"] <= 82
        assert controls_box["height"] <= 82
        assert toolbar_box["height"] <= 44
        assert provenance_box["y"] < toolbar_box["y"] + toolbar_box["height"]
        assert source_box["y"] < toolbar_box["y"] + toolbar_box["height"]
        assert canvas_box["y"] < 325
        assert canvas_wrap_box["y"] < rail_box["y"]
        assert bottom_strip_box["height"] <= 54
    finally:
        page.close()


def test_logic_builder_compact_topbar_controls_fit_at_1280(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 820})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        strip_box = page.locator("#logic-page-system-strip").bounding_box()
        controls_box = page.locator("#logic-command-controls").bounding_box()
        actions_box = page.locator("#logic-command-controls .logic-control-actions").bounding_box()
        process_box = page.locator("#logic-process").bounding_box()
        workflow_detail_box = page.locator("#logic-workflow-detail").bounding_box()
        provider_box = page.locator("#logic-provider").bounding_box()
        primary_box = page.locator("#logic-fault-next").bounding_box()
        back_box = page.locator("#logic-back").bounding_box()
        generation_stream_box = page.locator("#logic-generation-stream").bounding_box()
        stream_chunks_box = page.locator("#logic-stream-chunks").bounding_box()
        stream_chunk_box = page.locator("#logic-stream-chunks .stream-chunk").bounding_box()
        toolbar_box = page.locator("#logic-canvas-compact-toolbar").bounding_box()
        command_palette_box = page.locator("#logic-command-palette-open").bounding_box()
        mode_dock_box = page.locator("#logic-mode-dock").bounding_box()
        stream_box = page.locator("#logic-drawing-stream-timeline").bounding_box()
        canvas_box = page.locator("#logic-canvas").bounding_box()
        right_rail_box = page.locator("#logic-right-inspector-rail").bounding_box()
        bottom_strip_box = page.locator("#logic-bottom-run-strip").bounding_box()
        assert strip_box is not None
        assert controls_box is not None
        assert actions_box is not None
        assert process_box is not None
        assert workflow_detail_box is not None
        assert provider_box is not None
        assert primary_box is not None
        assert back_box is not None
        assert generation_stream_box is not None
        assert stream_chunks_box is not None
        assert stream_chunk_box is not None
        assert toolbar_box is not None
        assert command_palette_box is not None
        assert mode_dock_box is not None
        assert stream_box is not None
        assert canvas_box is not None
        assert right_rail_box is not None
        assert bottom_strip_box is not None
        assert strip_box["height"] <= 84
        assert actions_box["y"] + actions_box["height"] <= strip_box["y"] + strip_box["height"] - 1
        assert provider_box["y"] >= strip_box["y"] + 1
        assert primary_box["height"] <= 24
        assert primary_box["width"] >= 128
        assert controls_box["width"] >= 340
        assert workflow_detail_box["height"] >= 20
        assert page.locator("#logic-workflow-detail").evaluate(
            "el => el.scrollWidth <= el.clientWidth + 1 && el.scrollHeight <= el.clientHeight + 1"
        )
        assert page.locator("#logic-process").evaluate("el => el.scrollHeight <= el.clientHeight + 1")
        assert stream_chunks_box["y"] >= generation_stream_box["y"] + generation_stream_box["height"] - 1
        assert stream_chunks_box["y"] + stream_chunks_box["height"] <= process_box["y"] + process_box["height"] + 1
        assert stream_chunks_box["height"] <= 13
        assert stream_chunk_box["width"] >= stream_chunks_box["width"] - 2
        assert page.locator("#logic-stream-chunks .stream-chunk").evaluate("el => el.scrollWidth <= el.clientWidth + 1")
        assert toolbar_box["height"] <= 38
        assert page.locator("#logic-canvas-compact-toolbar").evaluate(
            "el => el.scrollHeight <= el.clientHeight + 1"
        )
        assert toolbar_box["y"] <= command_palette_box["y"] <= toolbar_box["y"] + 4
        assert command_palette_box["y"] + command_palette_box["height"] <= (
            toolbar_box["y"] + toolbar_box["height"] + 1
        )
        assert toolbar_box["y"] + toolbar_box["height"] <= mode_dock_box["y"] - 4
        assert stream_box["y"] >= mode_dock_box["y"] + mode_dock_box["height"] - 1
        assert stream_box["y"] + stream_box["height"] <= bottom_strip_box["y"] - 6
        fit_scale = float(page.locator("#logic-canvas").get_attribute("data-fit-scale") or "0")
        assert 0.92 <= fit_scale <= 0.97
        medium_circuit_graph_box = page.locator("#logic-canvas").evaluate(
            """() => {
              const canvas = document.querySelector("#logic-canvas")?.getBoundingClientRect();
              const rail = document.querySelector("#logic-right-inspector-rail")?.getBoundingClientRect();
              const boxes = Array.from(document.querySelectorAll(
                "#logic-canvas .logic-circuit-node, #logic-canvas .logic-circuit-gate, #logic-canvas .logic-output-node"
              )).map((node) => node.getBoundingClientRect()).filter((box) => box.width && box.height);
              if (!canvas || !rail || !boxes.length) return null;
              const graph = {
                bottom: Math.max(...boxes.map((box) => box.bottom)),
                right: Math.max(...boxes.map((box) => box.right)),
              };
              return {
                bottomGap: canvas.bottom - graph.bottom,
                rightRailGap: rail.left - graph.right,
              };
            }"""
        )
        assert medium_circuit_graph_box is not None
        assert medium_circuit_graph_box["bottomGap"] <= 205
        assert medium_circuit_graph_box["rightRailGap"] >= 40
        stream_toolbar_overlaps = page.evaluate(
            """() => {
              const stream = document.querySelector("#logic-drawing-stream-timeline")?.getBoundingClientRect();
              if (!stream) return ["missing-stream"];
              return Array.from(document.querySelectorAll("#logic-canvas-compact-toolbar button, #logic-canvas-compact-toolbar [id]"))
                .filter((element) => {
                  const box = element.getBoundingClientRect();
                  if (box.width === 0 || box.height === 0) return false;
                  return stream.left < box.right
                    && stream.right > box.left
                    && stream.top < box.bottom
                    && stream.bottom > box.top;
                })
                .map((element) => element.id || element.textContent?.trim() || element.tagName);
            }"""
        )
        assert stream_toolbar_overlaps == []
        stream_canvas_label_overlaps = page.evaluate(
            """() => {
              const stream = document.querySelector("#logic-drawing-stream-timeline")?.getBoundingClientRect();
              if (!stream) return ["missing-stream"];
              return Array.from(document.querySelectorAll(
                "#logic-circuit-svg .logic-circuit-column-label, #logic-reconstruction-mode-panel"
              ))
                .filter((element) => {
                  const box = element.getBoundingClientRect();
                  if (box.width === 0 || box.height === 0) return false;
                  return stream.left < box.right
                    && stream.right > box.left
                    && stream.top < box.bottom
                    && stream.bottom > box.top;
                })
                .map((element) => element.id || element.textContent?.trim() || element.tagName);
            }"""
        )
        assert stream_canvas_label_overlaps == []
        action_button_boxes = page.locator("#logic-command-controls button").evaluate_all(
            """nodes => nodes.map((node) => {
              const rect = node.getBoundingClientRect();
              return {
                y: rect.y,
                bottom: rect.y + rect.height,
                scrollHeight: node.scrollHeight,
                clientHeight: node.clientHeight,
                scrollWidth: node.scrollWidth,
                clientWidth: node.clientWidth
              };
            })"""
        )
        assert len(action_button_boxes) == 3
        assert max(box["y"] for box in action_button_boxes) - min(box["y"] for box in action_button_boxes) <= 1
        for box in action_button_boxes:
            assert box["bottom"] <= strip_box["y"] + strip_box["height"] - 1
            assert box["scrollHeight"] <= box["clientHeight"] + 1
            assert box["scrollWidth"] <= box["clientWidth"] + 1
        expect(page.locator("#logic-fault-next")).to_be_visible()
        expect(page.locator("#logic-back")).to_have_text("更多：返回需求")
    finally:
        page.close()


def test_logic_builder_cockpit_stream_replay_and_direct_annotations(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 960})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
              localStorage.removeItem("ai-fantui-logic-builder-annotation-batch-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        expect(page.locator("main.logic-cockpit-shell")).to_have_attribute("data-logic-experience", "cockpit-annotation-stream")
        expect(page.locator("main.logic-cockpit-shell")).to_have_attribute("data-ui-skin", "codex-minimal")
        expect(page.locator(".logic-cockpit-canopy")).to_be_hidden()
        expect(page.locator("#logic-canvas")).to_be_visible()
        expect(page.locator("#logic-drawing-stream-timeline")).to_be_visible()
        expect(page.locator("#logic-drawing-stream-timeline")).to_have_attribute("data-ai-stream", "logic-drawing-replay")
        expect(page.locator("#logic-drawing-stream-timeline")).to_have_attribute("data-blueprint39-stream", "compact-complete")
        expect(page.locator("#logic-drawing-stream-timeline .logic-stream-event")).to_have_count(8)
        expect(page.locator("#logic-drawing-stream-timeline")).to_contain_text("生成节点")
        expect(page.locator("#logic-drawing-stream-timeline")).to_contain_text("生成连线")
        expect(page.locator("#logic-drawing-stream-timeline")).to_contain_text("来源")
        stream_box = page.locator("#logic-drawing-stream-timeline").bounding_box()
        assert stream_box is not None
        assert stream_box["height"] <= 34
        stream_overlaps_nodes = page.evaluate(
            """() => {
              const stream = document.querySelector("#logic-drawing-stream-timeline");
              if (!stream) return [];
              const streamBox = stream.getBoundingClientRect();
              return Array.from(document.querySelectorAll(".logic-circuit-node")).filter((node) => {
                const box = node.getBoundingClientRect();
                return streamBox.left < box.right
                  && streamBox.right > box.left
                  && streamBox.top < box.bottom
                  && streamBox.bottom > box.top;
              }).map((node) => node.dataset.demoNodeId || node.dataset.nodeId || node.textContent.trim());
            }"""
        )
        assert stream_overlaps_nodes == []
        expect(page.locator("#logic-annotation-submit-bar")).to_be_hidden()

        canvas_box = page.locator("#logic-canvas").bounding_box()
        rail_box = page.locator("#logic-engineering-rail").bounding_box()
        assert canvas_box is not None
        assert canvas_box["y"] < 310
        if rail_box is not None:
            assert rail_box["y"] > canvas_box["y"]

        page.click('[data-demo-node-id="sw1"]')
        expect(page.locator("#logic-annotation-popover")).to_be_visible()
        expect(page.locator("#logic-annotation-submit-bar")).to_be_visible()
        expect(page.locator("#logic-bottom-provider")).to_be_visible()
        expect(page.locator("#logic-submit-annotations")).to_have_text("提交此次标注意见")
        expect(page.locator("#logic-submit-annotations")).to_be_disabled()
        expect(page.locator("#logic-selected-target-label")).to_contain_text("sw1")
        page.fill("#logic-node-comment-text", "SW1 节点需要补充来源锚点。")
        page.click("#logic-add-annotation")
        expect(page.locator("#logic-annotation-count")).to_have_text("1 条标注意见")
        expect(page.locator("#logic-annotation-list .logic-annotation-item")).to_have_count(1)

        page.click('.logic-circuit-wire[data-source="sw1"][data-target="logic1"]')
        expect(page.locator("#logic-selected-target-label")).to_contain_text("sw1 → logic1")
        page.fill("#logic-node-comment-text", "这条连线需要说明 SW1 如何进入 L1。")
        page.click("#logic-add-annotation")
        expect(page.locator("#logic-annotation-count")).to_have_text("2 条标注意见")
        expect(page.locator("#logic-annotation-list .logic-annotation-item")).to_have_count(2)
        expect(page.locator("#logic-submit-annotations")).to_be_enabled()
        page.click("#logic-submit-annotations")
        expect(page.locator("#logic-annotation-submit-state")).to_have_text("已提交 2 条标注意见")

        submitted = page.evaluate(
            """() => {
              const batch = JSON.parse(localStorage.getItem("ai-fantui-logic-builder-annotation-batch-v1"));
              return {
                count: batch.annotations.length,
                targets: batch.annotations.map((item) => `${item.target_type}:${item.target_id}`),
              };
            }"""
        )
        assert submitted["count"] == 2
        assert "node:sw1" in submitted["targets"]
        assert "wire:sw1->logic1" in submitted["targets"]
    finally:
        page.close()


def test_logic_builder_annotation_batch_calls_ai_revision_interpreter(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 960})
    captured_requests: list[dict[str, Any]] = []
    captured_updates: list[dict[str, Any]] = []
    try:
        page.route(
            "**/api/requirements-intake/interpret-logic-change",
            lambda route: (
                captured_requests.append(json.loads(route.request.post_data or "{}")),
                _fulfill_json(
                    route,
                    {
                        "kind": "ai-fantui-logic-change-interpretation",
                        "version": 1,
                        "status": "needs_user_confirmation",
                        "truth_effect": "none",
                        "candidate_state": "concept_logic_drawing_change",
                        "certification_claim": "none",
                        "controller_truth_modified": False,
                        "target_node_id": "sw1",
                        "annotation_text": "批量标注意见：SW1 节点需要补充来源锚点；sw1 → logic1 连线需要说明输入关系。",
                        "understanding_zh": "AI 已将两条标注归并为 SW1 到 L1 输入解释修订。",
                        "requirements_match_zh": "匹配 SW1/RA/L1 相关输入逻辑。",
                        "affected_nodes": ["sw1", "logic1"],
                        "affected_edges": ["sw1->logic1"],
                        "affected_parameter_panels": [],
                        "proposed_changes": ["补充 SW1 来源锚点。", "更新 sw1→logic1 连线说明。"],
                        "annotation_batch_summary_zh": "2 条标注意见归并为 1 个 SW1 输入解释修订包。",
                        "conflict_summary_zh": "未发现冲突。",
                        "annotation_groups": [
                            {
                                "group_label": "SW1 输入解释",
                                "annotation_ids": ["annotation_1", "annotation_2"],
                                "summary_zh": "节点和连线批注均指向 SW1 输入说明。",
                            }
                        ],
                        "selected_nodes": ["sw1"],
                        "selected_edges": ["sw1->logic1"],
                        "confirmation_question_zh": "是否确认按该批注包生成逻辑修订？",
                        "llm": {"provider": "deepseek", "model": "deepseek-v4-pro"},
                    },
                ),
            ),
        )
        page.route(
            "**/api/requirements-intake/update-logic-drawing",
            lambda route: (
                captured_updates.append(json.loads(route.request.post_data or "{}")),
                _fulfill_json(
                    route,
                    {
                        **_circuit_view_drawing(),
                        "summary_zh": "已按批量标注意见生成修订版逻辑电路图。",
                        "change_applied": {"source": "annotation_batch"},
                    },
                ),
            ),
        )
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-logic-builder-annotation-batch-v1");
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing()],
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        page.click('[data-demo-node-id="sw1"]')
        expect(page.locator("#logic-annotation-source")).not_to_have_text("选择节点或连线后显示来源。")
        expect(page.locator("#logic-annotation-params")).to_contain_text("角色：输入")
        expect(page.locator("#logic-annotation-params")).not_to_contain_text("role:")
        page.fill("#logic-node-comment-text", "SW1 节点需要补充来源锚点。")
        page.click("#logic-add-annotation")
        page.click('.logic-circuit-wire[data-source="sw1"][data-target="logic1"]')
        page.fill("#logic-node-comment-text", "这条连线需要说明 SW1 如何进入 L1。")
        page.click("#logic-add-annotation")
        page.click("#logic-submit-annotations")

        expect(page.locator("#logic-annotation-submit-state")).to_have_text("AI 已生成结构化修订建议")
        expect(page.locator("#logic-batch-interpretation-panel")).to_be_visible()
        expect(page.locator("#logic-batch-summary")).to_contain_text("2 条标注意见归并")
        expect(page.locator("#logic-batch-conflict-summary")).to_have_text("未发现冲突。")
        expect(page.locator("#logic-batch-proposed-changes li")).to_have_count(2)
        expect(page.locator("#logic-batch-confirmation-question")).to_contain_text("是否确认")
        expect(page.locator("#logic-batch-confirm-update")).to_be_enabled()

        assert len(captured_requests) == 1
        body = captured_requests[0]
        assert body["annotation_batch"][0]["target_type"] == "node"
        assert body["annotation_batch"][1]["target_type"] == "wire"
        assert body["selected_nodes"] == ["sw1"]
        assert body["selected_edges"] == ["sw1->logic1"]
        assert "批量标注意见" in body["annotation_text"]

        history_before = page.evaluate(
            """() => JSON.parse(localStorage.getItem("ai-fantui-logic-builder-change-history-v1") || "[]")"""
        )
        assert history_before[-1]["annotation_batch_count"] == 2
        assert history_before[-1]["status"] == "needs_confirmation"

        page.click("#logic-batch-confirm-update")
        expect(page.locator("#logic-process-title")).to_have_text("更新完成")
        expect(page.locator("#logic-batch-interpretation-panel")).to_be_hidden()
        assert len(captured_updates) == 1
        update_body = captured_updates[0]
        assert update_body["interpretation_payload"]["status"] == "confirmed_by_user"
        assert update_body["interpretation_payload"]["annotation_batch"][0]["target_id"] == "sw1"
        history_after = page.evaluate(
            """() => JSON.parse(localStorage.getItem("ai-fantui-logic-builder-change-history-v1") || "[]")"""
        )
        assert history_after[-1]["status"] == "updated"
    finally:
        page.close()


def test_logic_builder_combines_notes_change_and_history_into_tabbed_canvas_drawer(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 960})
    try:
        drawing = _circuit_view_drawing()
        drawing["drawing_notes"] = [
            *drawing["drawing_notes"],
            "truth_effect:none；controller_truth_modified:false。",
        ]
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            drawing,
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        expect(page.locator("#logic-workbench-drawers")).to_be_hidden()
        expect(page.locator(".logic-canvas-wrap > #logic-workbench-drawers")).to_be_hidden()
        expect(page.locator("aside.logic-inspector > details")).to_have_count(0)
        expect(page.locator("#logic-workbench-drawers")).to_have_attribute("data-active-tab", "none")
        expect(page.locator("#logic-detail-decision-board")).to_be_hidden()
        expect(page.locator("#logic-detail-decision-board .logic-detail-card")).to_have_count(3)
        expect(page.locator("#logic-workbench-drawers [role='tab']")).to_have_count(3)
        expect(page.locator("#logic-workbench-drawers > details")).to_have_count(0)
        expect(page.locator('#logic-workbench-drawers [aria-selected="true"]')).to_have_count(0)
        expect(page.locator("#logic-drawing-notes-details")).to_be_hidden()
        expect(page.locator("#logic-change-loop-details")).to_be_hidden()
        expect(page.locator("#logic-change-history-details")).to_be_hidden()

        canvas_box = page.locator("#logic-canvas").bounding_box()
        canvas_wrap_box = page.locator(".logic-canvas-wrap").bounding_box()
        assert canvas_box is not None
        assert canvas_wrap_box is not None
        assert canvas_wrap_box["height"] <= 800

        page.click('[data-demo-node-id="sw1"]')
        expect(page.locator("#logic-selected-node")).to_have_text("sw1")
        expect(page.locator("#logic-detail-selected-node")).to_have_text("sw1")
        expect(page.locator("#logic-workbench-drawers")).to_have_attribute("data-active-tab", "none")
        expect(page.locator("#logic-annotation-popover")).to_be_visible()
        expect(page.locator("#logic-change-loop-details")).to_be_hidden()
        expect(page.locator("#logic-drawing-notes-details")).to_be_hidden()

        page.click('#logic-collapsed-tool-rail [data-workbench-tab="notes"]')
        expect(page.locator("#logic-workbench-drawers")).to_have_attribute("data-active-tab", "notes")
        expect(page.locator("#logic-drawing-notes-details")).to_be_visible()
        expect(page.locator("#logic-annotation-popover")).to_be_hidden()
        logic_notes = page.locator("#logic-notes")
        for boundary in ["truth_effect:none", "controller_truth_modified:false"]:
            expect(logic_notes.locator(f'[data-boundary-token="{boundary}"]')).to_have_count(1)
            assert boundary not in logic_notes.inner_text()
        canvas_box_after_drawer = page.locator("#logic-canvas").bounding_box()
        drawer_box = page.locator("#logic-workbench-drawers").bounding_box()
        bottom_strip_box = page.locator("#logic-bottom-run-strip").bounding_box()
        assert canvas_box_after_drawer is not None
        assert drawer_box is not None
        assert bottom_strip_box is not None
        assert canvas_box_after_drawer["y"] + canvas_box_after_drawer["height"] <= drawer_box["y"] - 4
        assert drawer_box["y"] + drawer_box["height"] <= bottom_strip_box["y"] - 4
        drawer_covered_nodes = page.evaluate(
            """() => {
              const drawer = document.querySelector("#logic-workbench-drawers")?.getBoundingClientRect();
              if (!drawer) return ["missing-drawer"];
              return Array.from(document.querySelectorAll(".logic-circuit-node"))
                .filter((node) => {
                  const box = node.getBoundingClientRect();
                  if (box.width === 0 || box.height === 0) return false;
                  return drawer.left < box.right
                    && drawer.right > box.left
                    && drawer.top < box.bottom
                    && drawer.bottom > box.top;
                })
                .map((node) => node.dataset.demoNodeId || node.dataset.nodeId || node.textContent.trim());
            }"""
        )
        assert drawer_covered_nodes == []

        page.click('#logic-collapsed-tool-rail [data-workbench-tab="history"]')
        expect(page.locator("#logic-workbench-drawers")).to_have_attribute("data-active-tab", "history")
        expect(page.locator("#logic-workbench-drawers")).to_be_visible()
        expect(page.locator("#logic-change-history-details")).to_be_visible()
        expect(page.locator("#logic-change-loop-details")).to_be_hidden()
    finally:
        page.close()


def test_logic_builder_circuit_view_reduces_label_density_and_protects_sw_lane(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 900, "height": 760})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        expect(page.locator("#logic-circuit-eval-panel")).to_be_visible()
        expect(page.locator("#logic-canvas")).to_have_attribute("data-fit-mode", "fit-to-view")
        expect(page.locator("#logic-canvas")).to_have_attribute("data-readable-lanes", "sw")
        fit_scale = float(page.locator("#logic-canvas").get_attribute("data-fit-scale") or "0")
        assert 0.62 <= fit_scale <= 1

        expect(page.locator('[data-demo-node-id="sw1"]')).to_have_attribute("data-readable-lane", "sw")
        expect(page.locator('[data-demo-node-id="sw2"]')).to_have_attribute("data-readable-lane", "sw")
        expect(page.locator('[data-demo-node-id="sw1"]')).to_have_attribute("data-technical-id", "sw1")
        expect(page.locator('[data-demo-node-id="sw2"]')).to_have_attribute("data-technical-id", "sw2")
        expect(page.locator('[data-demo-node-id="sw1"] .logic-circuit-node-title')).to_have_text("SW1")
        expect(page.locator('[data-demo-node-id="sw2"] .logic-circuit-node-title')).to_have_text("SW2")
        assert "TRA" not in (page.locator('[data-demo-node-id="sw1"] .logic-circuit-node-title').text_content() or "")
        assert "TRA" not in (page.locator('[data-demo-node-id="sw2"] .logic-circuit-node-title').text_content() or "")

        sw1_title = page.locator('[data-demo-node-id="sw1"] title').text_content() or ""
        assert "显示标签：SW1" in sw1_title
        assert "技术 ID：sw1" in sw1_title
        assert "技术 id:" not in sw1_title
        assert "TRA [-1.4°,-6.2°]" in sw1_title
        expect(page.locator('[data-demo-node-id="sw1"] .logic-circuit-tech-id')).to_have_text("sw1")
        expect(page.locator('[data-demo-node-id="sw2"] .logic-circuit-tech-id')).to_have_text("sw2")

        expect(page.locator('.logic-circuit-lane-guide[data-readable-lane="sw"]')).to_have_count(1)
        expect(page.locator('.logic-circuit-lane-guide[data-readable-lane="sw"] .logic-circuit-lane-label')).to_have_text(
            "SW1/SW2 通道"
        )
        expect(page.locator('.logic-circuit-wire[data-source="sw1"][data-target="logic1"]')).to_have_attribute(
            "data-readable-lane",
            "sw",
        )
        expect(page.locator('.logic-circuit-wire[data-source="sw2"][data-target="logic2"]')).to_have_attribute(
            "data-readable-lane",
            "sw",
        )
        sw_wire_title = page.locator('.logic-circuit-wire[data-source="sw1"][data-target="logic1"] title').text_content() or ""
        assert "来源：" in sw_wire_title
        assert "来源:" not in sw_wire_title
        _assert_logic_circuit_blueprint_geometry(page)
    finally:
        page.close()


def test_logic_builder_circuit_view_provenance_legend_filters_node_sources(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 980, "height": 760})
    drawing = _circuit_view_drawing()
    view = drawing["circuit_view"]
    for node in view["nodes"]:
        if node["id"] == "radio_altitude_ft":
            node["source_anchors"] = [
                {
                    "id": "B37",
                    "kind": "正文条件",
                    "quote_zh": "无线电高度低于 6ft 时进入反推条件判断。",
                }
            ]
            break
    view["nodes"].append(
        {
            "id": "model_gap_probe",
            "label": "模型推断条件",
            "circuit_role": "input",
            "state": "idle",
            "x": 700,
            "y": 330,
            "width": 132,
            "height": 28,
        }
    )
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            drawing,
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        expect(page.locator("#logic-provenance-filter")).to_be_visible()
        expect(page.locator('[data-provenance-filter="source"] [data-provenance-count]')).to_have_text("1")
        expect(page.locator('[data-provenance-filter="local"] [data-provenance-count]')).to_have_text("19")
        expect(page.locator('[data-provenance-filter="assumption"] [data-provenance-count]')).to_have_text("1")
        expect(page.locator('[data-demo-node-id="radio_altitude_ft"]')).to_have_attribute("data-provenance-kind", "source")
        expect(page.locator('[data-demo-node-id="sw1"]')).to_have_attribute("data-provenance-kind", "local")
        expect(page.locator('[data-demo-node-id="model_gap_probe"]')).to_have_attribute("data-provenance-kind", "assumption")
        assert "来源：本地补齐" in (page.locator('[data-demo-node-id="sw1"] title').text_content() or "")

        page.click('[data-provenance-filter="assumption"]')
        expect(page.locator("#logic-canvas")).to_have_attribute("data-provenance-filter", "assumption")
        expect(page.locator('[data-demo-node-id="model_gap_probe"]')).to_have_class(re.compile(r"is-provenance-match"))
        expect(page.locator('[data-demo-node-id="sw1"]')).to_have_class(re.compile(r"is-provenance-muted"))

        page.click('[data-provenance-filter="source"]')
        expect(page.locator("#logic-canvas")).to_have_attribute("data-provenance-filter", "source")
        expect(page.locator('[data-demo-node-id="radio_altitude_ft"]')).to_have_class(re.compile(r"is-provenance-match"))
        expect(page.locator('[data-demo-node-id="model_gap_probe"]')).to_have_class(re.compile(r"is-provenance-muted"))

        page.click('[data-provenance-filter="all"]')
        expect(page.locator("#logic-canvas")).to_have_attribute("data-provenance-filter", "all")
        expect(page.locator('[data-demo-node-id="model_gap_probe"]')).not_to_have_class(re.compile(r"is-provenance-muted"))
    finally:
        page.close()


def test_logic_builder_unknown_circuit_state_uses_readable_fallback(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 980, "height": 760})
    drawing = _circuit_view_drawing()
    view = drawing["circuit_view"]
    view["nodes"].append(
        {
            "id": "state_probe",
            "label": "状态探针",
            "circuit_role": "input",
            "state": "backend_pending_raw",
            "x": 700,
            "y": 330,
            "width": 132,
            "height": 28,
        }
    )
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            drawing,
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        state_probe = page.locator('[data-demo-node-id="state_probe"]')
        expect(state_probe).to_have_attribute("data-state", "idle")
        stored_state = page.evaluate(
            """() => {
              const drawing = JSON.parse(localStorage.getItem("ai-fantui-logic-builder-drawing-v1"));
              return drawing.circuit_view.nodes.find((node) => node.id === "state_probe").state;
            }"""
        )
        assert stored_state == "backend_pending_raw"
        page.click('[data-demo-node-id="state_probe"]')
        expect(page.locator("#logic-annotation-params")).to_contain_text("状态：状态待确认")
        expect(page.locator("#logic-annotation-params")).not_to_contain_text("backend_pending_raw")
    finally:
        page.close()


def test_logic_builder_unknown_circuit_role_uses_readable_fallback(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 980, "height": 760})
    drawing = _circuit_view_drawing()
    view = drawing["circuit_view"]
    view["nodes"].append(
        {
            "id": "role_probe",
            "label": "角色探针",
            "circuit_role": "backend_role_raw",
            "state": "idle",
            "x": 700,
            "y": 360,
            "width": 132,
            "height": 28,
        }
    )
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            drawing,
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        role_probe = page.locator('[data-demo-node-id="role_probe"]')
        expect(role_probe).to_have_attribute("data-circuit-role", "backend_role_raw")
        page.click('[data-demo-node-id="role_probe"]')
        expect(page.locator("#logic-annotation-params")).to_contain_text("角色：角色待确认")
        expect(page.locator("#logic-annotation-params")).not_to_contain_text("backend_role_raw")
    finally:
        page.close()


def test_deepseek_live_replay_import_seeds_workbench_without_model_calls(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    model_calls: list[str] = []
    try:
        page.route("**/api/requirements-intake/deepseek-live-demo-replay", lambda route: _fulfill_json(route, _replay_payload()))

        def reject_model_call(route: Any) -> None:
            model_calls.append(route.request.url)
            route.fulfill(status=500, content_type="application/json", body='{"error":"model_call_forbidden"}')

        page.route("**/api/requirements-intake/analyze", reject_model_call)
        page.route("**/api/requirements-intake/draw-logic", reject_model_call)
        page.route("**/api/requirements-intake/prepare-fault-injection", reject_model_call)
        page.route("**/api/requirements-intake/prepare-fault-injection/sandbox", reject_model_call)

        page.goto(f"{demo_server}/index.html", wait_until="networkidle")
        expect(page.locator("#deepseek-live-replay-import")).to_be_visible()
        expect(page.locator("#deepseek-live-replay-meta")).to_contain_text("deepseek-v4-pro")
        expect(page.locator("#deepseek-live-replay-meta")).to_contain_text("2026-05-13 10:30")
        expect(page.locator("#deepseek-live-replay-counts")).to_contain_text("需求理解")
        expect(page.locator("#deepseek-live-replay-counts")).to_contain_text("沙盒计划")
        expect(page.locator("#deepseek-live-replay-counts")).to_contain_text("1 plans")
        page.click("#deepseek-live-replay-import")
        page.wait_for_url("**/fault-injection-sandbox?replay=deepseek-live")
        expect(page.locator("#fault-sandbox-result-state")).to_have_text("配置已生成")
        expect(page.locator("#fault-sandbox-plan-coverage-evidence")).to_contain_text("auto_fault_thr_lock_rel")
        expect(page.locator("#fault-sandbox-source-metrics")).to_contain_text("2 已回答")
        stored = page.evaluate(
            """
            () => ({
              requirements: JSON.parse(localStorage.getItem("ai-fantui-requirements-intake-ready-v1")).kind,
              drawing: JSON.parse(localStorage.getItem("ai-fantui-logic-builder-drawing-v1")).kind,
              drawingHasCircuitView: Boolean(JSON.parse(localStorage.getItem("ai-fantui-logic-builder-drawing-v1")).circuit_view),
              history: JSON.parse(localStorage.getItem("ai-fantui-logic-builder-change-history-v1")).length,
              faultAnswers: JSON.parse(localStorage.getItem("ai-fantui-fault-injection-preparation-v1")).boundary_answers.length,
              sandbox: JSON.parse(localStorage.getItem("ai-fantui-fault-injection-sandbox-plan-v1")).kind,
            })
            """
        )
        assert stored == {
            "requirements": "ai-fantui-requirements-intake-analysis",
            "drawing": "ai-fantui-logic-link-drawing",
            "drawingHasCircuitView": True,
            "history": 0,
            "faultAnswers": 2,
            "sandbox": "ai-fantui-fault-injection-sandbox-plan",
        }
        assert model_calls == []
        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        _show_logic_builder_workbench(page)
        expect(page.locator("#logic-circuit-eval-panel")).to_be_visible()
        page.select_option("#logic-circuit-preset-select", "max-reverse")
        expect(page.locator("#logic-circuit-status-badge")).to_have_text("已放出")
        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        expect(page.locator("#requirements-status")).to_have_text("已恢复回放草稿")
        expect(page.locator("#result-state")).to_have_text("可进入逻辑链路")
        expect(page.locator("#graph-counts")).to_have_text("3 nodes · 2 edges")
        _screenshot(page, "06-deepseek-live-replay-import")
    finally:
        page.close()


def test_deepseek_live_replay_file_mode_explains_local_server_requirement(browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 820})
    replay_api_requests: list[str] = []

    def collect_replay_api_request(request: Any) -> None:
        if "/api/requirements-intake/deepseek-live-demo-replay" in request.url:
            replay_api_requests.append(request.url)

    page.on("request", collect_replay_api_request)
    try:
        page.goto((Path("src/well_harness/static/index.html").resolve()).as_uri(), wait_until="networkidle")
        expect(page.locator("#deepseek-live-replay-import")).to_be_visible()
        expect(page.locator("#deepseek-live-replay-status")).to_contain_text("请从本地服务入口打开")
        expect(page.locator("#deepseek-live-replay-meta")).to_contain_text("需启动本地服务")
        expect(page.locator("#deepseek-live-replay-counts")).to_contain_text("浏览器文件模式不能读取本地回放")

        page.click("#deepseek-live-replay-import")
        expect(page.locator("#deepseek-live-replay-status")).to_contain_text("请先从本地服务入口打开")
        expect(page.locator("#deepseek-live-replay-status")).not_to_contain_text("Failed to fetch")
        assert replay_api_requests == []
    finally:
        page.close()
