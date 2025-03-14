# Author: Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2023, Ansible Project
"""
MarkDown serialization.
"""

from __future__ import annotations

import re
import typing as t

from . import dom
from .format import Formatter, LinkProvider
from .format import format_paragraphs as _format_paragraphs
from .html import _url_escape
from .html import html_escape as _html_escape

_MD_ESCAPE = re.compile(r"""([!"#$%&'()*+,:;<=>?@[\\\]^_`{|}~.-])""")


def md_escape(text: str) -> str:
    return _MD_ESCAPE.sub(r"\\\1", text)


class MDFormatter(Formatter):
    @staticmethod
    def _format_option_like(
        part: dom.OptionNamePart | dom.ReturnValuePart, url: str | None
    ) -> str:
        link_start = ""
        link_end = ""
        if url:
            link_start = f'<a href="{_html_escape(_url_escape(url))}">'
            link_end = "</a>"
        strong_start = ""
        strong_end = ""
        if part.type == dom.PartType.OPTION_NAME and part.value is None:
            strong_start = "<strong>"
            strong_end = "</strong>"
        if part.value is None:
            text = part.name
        else:
            text = f"{part.name}={part.value}"
        return f"<code>{strong_start}{link_start}{md_escape(text)}{link_end}{strong_end}</code>"

    def format_error(self, part: dom.ErrorPart) -> str:
        return f"<b>ERROR while parsing</b>: {md_escape(part.message)}"

    def format_bold(self, part: dom.BoldPart) -> str:
        return f"<b>{md_escape(part.text)}</b>"

    def format_code(self, part: dom.CodePart) -> str:
        return f"<code>{md_escape(part.text)}</code>"

    def format_horizontal_line(self, part: dom.HorizontalLinePart) -> str:
        return "<hr>"

    def format_italic(self, part: dom.ItalicPart) -> str:
        return f"<em>{md_escape(part.text)}</em>"

    def format_link(self, part: dom.LinkPart) -> str:
        url_escaped = md_escape(_url_escape(part.url))
        return f"[{md_escape(part.text)}]({url_escaped})"

    def format_module(self, part: dom.ModulePart, url: str | None) -> str:
        if url:
            return f"[{md_escape(part.fqcn)}]({md_escape(_url_escape(url))})"
        return md_escape(part.fqcn)

    def format_rst_ref(self, part: dom.RSTRefPart) -> str:
        return md_escape(part.text)

    def format_url(self, part: dom.URLPart) -> str:
        url_escaped = md_escape(_url_escape(part.url))
        return f"[{md_escape(part.url)}]({url_escaped})"

    def format_text(self, part: dom.TextPart) -> str:
        return md_escape(part.text)

    def format_env_variable(self, part: dom.EnvVariablePart) -> str:
        return f"<code>{md_escape(part.name)}</code>"

    def format_option_name(self, part: dom.OptionNamePart, url: str | None) -> str:
        return self._format_option_like(part, url)

    def format_option_value(self, part: dom.OptionValuePart) -> str:
        return f"<code>{md_escape(part.value)}</code>"

    def format_plugin(self, part: dom.PluginPart, url: str | None) -> str:
        if url:
            return f"[{md_escape(part.plugin.fqcn)}]({md_escape(_url_escape(url))})"
        return md_escape(part.plugin.fqcn)

    def format_return_value(self, part: dom.ReturnValuePart, url: str | None) -> str:
        return self._format_option_like(part, url)


DEFAULT_FORMATTER = MDFormatter()


def postprocess_md_paragraph(par: str) -> str:
    lines = par.strip().splitlines()
    lines = [line.strip().replace("\t", " ") for line in lines]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def to_md(
    paragraphs: t.Sequence[dom.Paragraph],
    formatter: Formatter = DEFAULT_FORMATTER,
    link_provider: LinkProvider | None = None,
    par_start: str = "",
    par_end: str = "",
    par_sep: str = "\n\n",
    par_empty: str = " ",
    current_plugin: dom.PluginIdentifier | None = None,
) -> str:
    return _format_paragraphs(
        paragraphs,
        formatter=formatter,
        link_provider=link_provider,
        par_start=par_start,
        par_end=par_end,
        par_sep=par_sep,
        par_empty=par_empty,
        current_plugin=current_plugin,
        postprocess_paragraph=postprocess_md_paragraph,
    )
