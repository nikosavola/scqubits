# explorer_settings.py
#
# This file is part of scqubits: a Python package for superconducting qubits,
# Quantum 5, 583 (2021). https://quantum-journal.org/papers/q-2021-11-17-583/
#
#    Copyright (c) 2019 and later, Jens Koch and Peter Groszkowski
#    All rights reserved.
#
#    This source code is licensed under the BSD-style license found in the
#    LICENSE file in the root directory of this source tree.
############################################################################

from typing import TYPE_CHECKING, Any, Dict

import scqubits as scq
import scqubits.ui.gui_custom_widgets as ui

from scqubits.ui.gui_defaults import PlotType, mode_dropdown_list
from scqubits.utils import misc as utils


if TYPE_CHECKING:
    from scqubits.ui.explorer_widget import PlotID
    from scqubits import Explorer

try:
    from IPython.display import display, HTML, notebook
except ImportError:
    _HAS_IPYTHON = False
else:
    _HAS_IPYTHON = True

try:
    import ipyvuetify as v
    import ipywidgets
    from scqubits.ui.gui_custom_widgets import flex_row
except ImportError:
    _HAS_IPYVUETIFY = False
else:
    _HAS_IPYVUETIFY = True


class ExplorerSettings:
    """
    Generates the UI for Explorer settings.

    Parameters
    ----------
    explorer:
        the `Explorer` object of interest

    Attributes
    ----------
    ui:
        dictionary of all UI elements
    """

    @utils.Required(ipyvuetify=_HAS_IPYVUETIFY)
    def __init__(self, explorer: "Explorer"):
        self.explorer = explorer
        self.ui: Dict[str, Any] = {}
        self.ui["level_slider"]: Dict[PlotID, v.VuetifyWidget] = {}
        self.ui["Transitions"]: Dict[str, v.VuetifyWidget] = {}

        for plot_id in self.explorer.ui["panel_switch_by_plot_id"].keys():
            self.ui[plot_id] = self.build_ui(plot_id)

        self.ui["dialogs"] = {
            plot_id: v.Dialog(
                v_model=False,
                width="40%",
                children=[
                    v.Card(
                        children=[
                            v.Toolbar(
                                children=[
                                    v.ToolbarTitle(
                                        children=[f"Plot settings: {str(plot_id)}"]
                                    )
                                ],
                                color="deep-purple accent-4",
                                dark=True,
                            ),
                            v.CardText(children=[ui.flex_row(self.ui[plot_id])]),
                        ]
                    )
                ],
            )
            for plot_id in self.explorer.ui["panel_switch_by_plot_id"].keys()
        }

    def __getitem__(self, item):
        return self.ui[item]

    def build_ui(self, plot_id: "PlotID"):
        subsys = plot_id.subsystems
        plot_type = plot_id.plot_type

        if plot_type == PlotType.ENERGY_SPECTRUM:
            subsys = subsys[0]
            subsys_index = self.explorer.sweep.get_subsys_index(subsys)
            evals_count = self.explorer.sweep.subsys_evals_count(subsys_index)
            self.ui["level_slider"][plot_id] = ui.vNumberEntryWidget(
                num_type=int,
                label="Highest level",
                v_min=1,
                v_max=evals_count,
                v_model=evals_count,
                text_kwargs={
                    "style_": "min-width: 140px; max-width: 200px;",
                    "dense": True,
                },
                slider_kwargs={
                    "style_": "min-width: 110px; max-width: 230px",
                    "dense": True,
                },
            )
            ui_subtract_ground_switch = v.Switch(
                label="Subtract E\u2080", v_model=True, width=300
            )
            self.ui["level_slider"][plot_id].observe(
                self.explorer.update_plots, names="v_model"
            )
            ui_subtract_ground_switch.observe(
                self.explorer.update_plots, names="v_model"
            )
            return [
                self.ui["level_slider"][plot_id].widget(),
                ui_subtract_ground_switch,
            ]

        if plot_type == PlotType.WAVEFUNCTIONS:
            subsys = subsys[0]
            if isinstance(
                subsys, (scq.FluxQubit, scq.ZeroPi, scq.Bifluxon, scq.Cos2PhiQubit)
            ):
                ui_wavefunction_selector = ui.vInitSelect(
                    label="Display wavefunctions",
                    items=list(range(subsys.truncated_dim)),
                    v_model=0,
                )
            else:
                ui_wavefunction_selector = ui.vInitSelect(
                    label="Display wavefunctions",
                    multiple=True,
                    items=list(range(subsys.truncated_dim)),
                    v_model=list(range(5)),
                )
            ui_mode_dropdown = ui.vInitSelect(
                items=mode_dropdown_list,
                v_model=mode_dropdown_list[0],
                label="Plot amplitude as",
            )
            ui_wavefunction_selector.observe(
                self.explorer.update_plots, names="v_model"
            )
            ui_mode_dropdown.observe(self.explorer.update_plots, names="v_model")
            return [ui_wavefunction_selector, ui_mode_dropdown]

        if plot_type == PlotType.MATRIX_ELEMENTS:
            subsys = subsys[0]
            ui_mode_dropdown = ui.vInitSelect(
                items=mode_dropdown_list,
                label="Plot matrix elements as",
                v_model=mode_dropdown_list[2],
            )
            op_names = subsys.get_operator_names()
            ui_operator_dropdown = ui.vInitSelect(
                items=op_names, label="Operator", v_model=op_names[0]
            )
            ui_mode_dropdown.observe(self.explorer.update_plots, names="v_model")
            ui_operator_dropdown.observe(self.explorer.update_plots, names="v_model")
            return [ui_mode_dropdown, ui_operator_dropdown]

        if plot_type == PlotType.MATRIX_ELEMENT_SCAN:
            subsys = subsys[0]
            ui_mode_dropdown = ui.vInitSelect(
                items=mode_dropdown_list,
                label="Plot matrix elements as",
                v_model=mode_dropdown_list[2],
            )
            op_names = subsys.get_operator_names()
            ui_operator_dropdown = ui.vInitSelect(
                items=op_names, label="Operator", v_model=op_names[0]
            )
            ui_mode_dropdown.observe(self.explorer.update_plots, names="v_model")
            ui_operator_dropdown.observe(self.explorer.update_plots, names="v_model")
            return [ui_mode_dropdown, ui_operator_dropdown]

        if plot_type == PlotType.TRANSITIONS:
            self.ui["Transitions"]["initial_state_inttexts"] = [
                ui.vValidatedNumberField(
                    label=subsys.id_str,
                    num_type=int,
                    v_min=0,
                    v_max=subsys.truncated_dim,
                    v_model=0,
                    style_="display: inherit; width: 65px;",
                    class_="ml-4",
                )
                for subsys in self.explorer.sweep.hilbertspace
            ]

            self.ui["Transitions"][
                "initial_dressed_inttext"
            ] = ui.vValidatedNumberField(
                label="Dressed state",
                class_="ml-4 align-bottom",
                num_type=int,
                v_min=0,
                v_max=self.explorer.sweep.hilbertspace.dimension,
                v_model=0,
                style_="display: none; width: 65px;",
            )

            self.ui["Transitions"]["photons_inttext"] = ui.vValidatedNumberField(
                num_type=int,
                class_="ml-3",
                v_model=1,
                v_min=1,
                v_max=5,
                label="Photon number",
                style_="max-width: 120px",
            )
            self.ui["Transitions"]["highlight_selectmultiple"] = ui.vInitSelect(
                multiple=True,
                label="",
                items=self.explorer.subsys_names,
                v_model=[self.explorer.subsys_names[0]],
                width=185,
            )

            self.ui["Transitions"]["initial_bare_dressed_toggle"] = v.RadioGroup(
                v_model="bare",
                children=[
                    v.Radio(label="by bare product label", value="bare"),
                    v.Radio(label="by dressed index", value="dressed"),
                ],
            )

            self.ui["Transitions"]["sidebands_switch"] = v.Switch(
                label="Show sidebands", v_model=False, width=250
            )
            for inttext in self.ui["Transitions"]["initial_state_inttexts"]:
                inttext.observe(self.explorer.update_plots, names="num_value")
            self.ui["Transitions"]["initial_dressed_inttext"].observe(
                self.explorer.update_plots, names="num_value"
            )
            self.ui["Transitions"]["photons_inttext"].observe(
                self.explorer.update_plots, names="num_value"
            )
            self.ui["Transitions"]["highlight_selectmultiple"].observe(
                self.explorer.update_plots, names="v_model"
            )
            self.ui["Transitions"]["sidebands_switch"].observe(
                self.explorer.update_plots, names="v_model"
            )
            self.ui["Transitions"]["initial_bare_dressed_toggle"].observe(
                self.explorer.bare_dressed_toggle, names="v_model"
            )

            initial_state_selection = ui.flex_row(
                [
                    v.Text(children=["Initial state"]),
                    self.ui["Transitions"]["initial_bare_dressed_toggle"],
                    *self.ui["Transitions"]["initial_state_inttexts"],
                    self.ui["Transitions"]["initial_dressed_inttext"],
                ]
            )

            photon_options_selection = v.Container(
                class_="d-flex flex-row",
                children=[
                    v.Text(children=["Single vs. multi-photon transitions"]),
                    self.ui["Transitions"]["photons_inttext"],
                ],
            )
            transition_highlighting = v.Container(
                class_="d-flex flex-row",
                children=[
                    v.Text(children=["Highlight:"]),
                    self.ui["Transitions"]["highlight_selectmultiple"],
                ],
            )

            return [
                v.Container(
                    class_="d-flex flex-column",
                    children=[
                        initial_state_selection,
                        photon_options_selection,
                        self.ui["Transitions"]["sidebands_switch"],
                        transition_highlighting,
                    ],
                ),
            ]

        if plot_type in [PlotType.CROSS_KERR, PlotType.AC_STARK]:
            self.ui["kerr"] = {}
            # self.ui["kerr"]["subsys1"] = ui.vInitSelect(
            #     multiple=False,
            #     label="Subsystem 1",
            #     items=plot_id.subsystems,
            #     v_model=self.explorer.subsys_names[0],
            #     width=185,
            # )
            # self.ui["kerr"]["subsys2"] = ui.vInitSelect(
            #     multiple=False,
            #     label="Subsystem 2",
            #     items=self.explorer.subsys_names,
            #     v_model=self.explorer.subsys_names[0],
            #     width=185,
            # )
            #
            # import IPython
            # self.ui["kerr"]["latex"] = ipywidgets.Output()
            # self.ui["kerr"]["latex"].append_display_data(
            #     IPython.display.Math(
            #         r"\chi_l \hat{a}^\dagger \hat{a} |l\rangle\langle l|,\quad"
            #         r" K \hat{a}^\dagger \hat{a} \hat{b}^\dagger \hat{b}"
            #     )
            # )

            self.ui["kerr"]["ac_stark_ell"] = ui.vValidatedNumberField(
                num_type=int,
                class_="ml-3",
                v_model=1,
                v_min=1,
                v_max=5,
                label="l (qubit level)",
                style_="max-width: 120px; display: none;",
            )

            return [
                v.Container(
                    class_="d-flex flex-column",
                    children=[
                        # self.ui["kerr"]["latex"],
                        ui.flex_row(
                            [
                                # [self.ui["kerr"]["subsys1"], self.ui["kerr"]["subsys2"],
                                self.ui["kerr"]["ac_stark_ell"]
                            ]
                        ),
                    ],
                ),
            ]

        return []
