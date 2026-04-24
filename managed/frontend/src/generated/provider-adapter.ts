import Button from "primevue/button";
import Card from "primevue/card";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import Dialog from "primevue/dialog";
import Drawer from "primevue/drawer";
import Fieldset from "primevue/fieldset";
import FloatLabel from "primevue/floatlabel";
import InputGroup from "primevue/inputgroup";
import InputText from "primevue/inputtext";
import Message from "primevue/message";
import Paginator from "primevue/paginator";
import Panel from "primevue/panel";
import ProgressSpinner from "primevue/progressspinner";
import Select from "primevue/select";
import Tabs from "primevue/tabs";
import Toolbar from "primevue/toolbar";

export const publicPrimeVueProviderComponents = {
  "UiButton": {
    componentId: "UiButton",
    implementationRef: "Button",
    packageRef: "primevue/button",
    component: Button,
    alignmentNotes: [
  "maps Kernel action semantics onto PrimeVue Button",
],
  },
  "UiInput": {
    componentId: "UiInput",
    implementationRef: "InputText",
    packageRef: "primevue/inputtext",
    component: InputText,
    alignmentNotes: [
  "maps Kernel text input semantics onto PrimeVue InputText",
],
  },
  "UiSelect": {
    componentId: "UiSelect",
    implementationRef: "Select",
    packageRef: "primevue/select",
    component: Select,
    alignmentNotes: [
  "maps Kernel selection semantics onto PrimeVue Select",
],
  },
  "UiForm": {
    componentId: "UiForm",
    implementationRef: "Fieldset",
    packageRef: "primevue/fieldset",
    component: Fieldset,
    alignmentNotes: [
  "uses PrimeVue Fieldset as the governed form container shell",
],
  },
  "UiFormItem": {
    componentId: "UiFormItem",
    implementationRef: "FloatLabel",
    packageRef: "primevue/floatlabel",
    component: FloatLabel,
    alignmentNotes: [
  "uses PrimeVue FloatLabel to keep field label semantics explicit",
],
  },
  "UiTable": {
    componentId: "UiTable",
    implementationRef: "DataTable",
    packageRef: "primevue/datatable",
    component: DataTable,
    alignmentNotes: [
  "maps Kernel structured list semantics onto PrimeVue DataTable",
],
  },
  "UiDialog": {
    componentId: "UiDialog",
    implementationRef: "Dialog",
    packageRef: "primevue/dialog",
    component: Dialog,
    alignmentNotes: [
  "maps Kernel modal confirmation semantics onto PrimeVue Dialog",
],
  },
  "UiDrawer": {
    componentId: "UiDrawer",
    implementationRef: "Drawer",
    packageRef: "primevue/drawer",
    component: Drawer,
    alignmentNotes: [
  "maps Kernel side panel semantics onto PrimeVue Drawer",
],
  },
  "UiEmpty": {
    componentId: "UiEmpty",
    implementationRef: "Message",
    packageRef: "primevue/message",
    component: Message,
    alignmentNotes: [
  "uses PrimeVue Message to keep empty-state feedback visible",
],
  },
  "UiSpinner": {
    componentId: "UiSpinner",
    implementationRef: "ProgressSpinner",
    packageRef: "primevue/progressspinner",
    component: ProgressSpinner,
    alignmentNotes: [
  "maps Kernel loading semantics onto PrimeVue ProgressSpinner",
],
  },
  "UiPageHeader": {
    componentId: "UiPageHeader",
    implementationRef: "Toolbar",
    packageRef: "primevue/toolbar",
    component: Toolbar,
    alignmentNotes: [
  "uses PrimeVue Toolbar to keep page header actions semantically partitioned",
],
  },
  "UiTabs": {
    componentId: "UiTabs",
    implementationRef: "Tabs",
    packageRef: "primevue/tabs",
    component: Tabs,
    alignmentNotes: [
  "maps Kernel segmented navigation semantics onto PrimeVue Tabs",
],
  },
  "UiSearchBar": {
    componentId: "UiSearchBar",
    implementationRef: "InputGroup",
    packageRef: "primevue/inputgroup",
    component: InputGroup,
    alignmentNotes: [
  "uses PrimeVue InputGroup for governed search input plus trigger composition",
],
  },
  "UiFilterBar": {
    componentId: "UiFilterBar",
    implementationRef: "Toolbar",
    packageRef: "primevue/toolbar",
    component: Toolbar,
    alignmentNotes: [
  "uses PrimeVue Toolbar to keep filter controls grouped and governed",
],
  },
  "UiResult": {
    componentId: "UiResult",
    implementationRef: "Message",
    packageRef: "primevue/message",
    component: Message,
    alignmentNotes: [
  "uses PrimeVue Message for structured success and partial-error feedback",
],
  },
  "UiSection": {
    componentId: "UiSection",
    implementationRef: "Panel",
    packageRef: "primevue/panel",
    component: Panel,
    alignmentNotes: [
  "uses PrimeVue Panel to preserve explicit page section boundaries",
],
  },
  "UiToolbar": {
    componentId: "UiToolbar",
    implementationRef: "Toolbar",
    packageRef: "primevue/toolbar",
    component: Toolbar,
    alignmentNotes: [
  "maps Kernel in-page action cluster semantics onto PrimeVue Toolbar",
],
  },
  "UiPagination": {
    componentId: "UiPagination",
    implementationRef: "Paginator",
    packageRef: "primevue/paginator",
    component: Paginator,
    alignmentNotes: [
  "maps Kernel result-set navigation semantics onto PrimeVue Paginator",
],
  },
  "UiCard": {
    componentId: "UiCard",
    implementationRef: "Card",
    packageRef: "primevue/card",
    component: Card,
    alignmentNotes: [
  "maps Kernel structured info block semantics onto PrimeVue Card",
],
  },
} as const;

export const publicPrimeVueProviderHelpers = {
  Column,
} as const;
