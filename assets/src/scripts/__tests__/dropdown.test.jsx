import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { Select } from "../Components/Select";

const props = {
  choices: [
    { label: "---", value: "", organisation: "OpenSAFELY" },
    {
      label: "Abdominal aortic aneurysm diagnosis codes",
      value: "nhsd-primary-care-domain-refsets/aaa_cod/20210127",
      organisation: "NHSD Primary Care Domain Refsets",
    },
    {
      label: "Active and inactive ethnicity codes",
      value: "nhsd-primary-care-domain-refsets/ethnall_cod/20210127",
      organisation: "NHSD Primary Care Domain Refsets",
    },
    {
      label: "Alanine aminotransferase (ALT) tests",
      value: "opensafely/alanine-aminotransferase-alt-tests/2298df3e",
      organisation: "OpenSAFELY",
    },
    {
      label: "Alanine aminotransferase (ALT) tests (numerical value)",
      value:
        "opensafely/alanine-aminotransferase-alt-tests-numerical-value/78d4a307",
      organisation: "OpenSAFELY",
    },
    {
      label: "All BMI coded terms",
      value: "primis-covid19-vacc-uptake/bmi_stage/v1.2",
      organisation: "PRIMIS Covid Vaccination Uptake Reporting",
    },
  ],
  data: {
    choices: "react-dropdown-options",
    errors: "react-dropdown-errors",
    hint: "Codelists are published by OpenSAFELY on OpenCodelists and use the SNOMED CT coding system",
    id: "codelist_slug",
    label: "Codelists",
    name: "codelist_slug",
  },
  errors: [],
};

describe("Native <select> component", () => {
  const user = userEvent.setup();

  it("updates the value based on state", async () => {
    render(<Select {...props} />);

    const select = screen.getByTestId(props.data.name);
    expect(select.options.length).toBe(props.choices.length);
    expect(select.options[select.selectedIndex].value).toBeUndefined;

    const combobox = screen.getByRole("combobox");
    await user.type(combobox, props.choices[1].label);
    expect(combobox.value).toBe(props.choices[1].label);
    await user.click(screen.getByRole("option"));
    expect(select.options[select.selectedIndex].value).toBe(
      props.choices[1].value
    );
  });

  test("Text input displays a list of matching choices", async () => {
    render(<Select {...props} />);

    await user.type(
      screen.getByRole("combobox"),
      props.choices[4].label.slice(0, 6)
    );
    expect(screen.getAllByRole("option").length).toBe(2);
    await user.clear(screen.getByRole("combobox"));
    await user.type(screen.getByRole("combobox"), props.choices[1].label);
    expect(screen.getByRole("option").textContent).toBe(
      `${props.choices[1].label}, From: ${props.choices[1].organisation}`
    );
  });

  test("Selected item gets a highlighted class", async () => {
    const { container } = render(<Select {...props} />);

    await user.type(screen.getByRole("combobox"), props.choices[1].label);
    expect(screen.getByRole("option").textContent).toBe(
      `${props.choices[1].label}, From: ${props.choices[1].organisation}`
    );

    await user.click(screen.getByRole("option"));

    const select = screen.getByTestId(props.data.name);
    expect(select.options[select.selectedIndex].value).toBe(
      props.choices[1].value
    );
    expect(screen.getByRole("combobox").value).toBe(props.choices[1].label);

    await user.click(screen.getByRole("combobox"));
    await user.type(screen.getByRole("combobox"), "{Backspace}");
    await waitFor(() =>
      expect(screen.getByRole("option").textContent).toBe(
        `${props.choices[1].label}, From: ${props.choices[1].organisation}`
      )
    );
    expect(container.querySelector('[role="option"]')).toHaveClass(
      "bg-oxford-100 font-bold"
    );
  });

  test("Selected item gets remove on clear selection click", async () => {
    render(<Select {...props} />);

    await user.type(screen.getByRole("combobox"), props.choices[1].label);
    expect(screen.getByRole("option").textContent).toBe(
      `${props.choices[1].label}, From: ${props.choices[1].organisation}`
    );

    await user.click(screen.getByRole("option"));

    const select = screen.getByTestId(props.data.name);
    expect(select.options[select.selectedIndex].value).toBe(
      props.choices[1].value
    );

    await user.click(screen.getByRole("button", { name: "Clear selection" }));
    await user.click(screen.getByRole("button", { name: "Show dropdown" }));
    expect(select.options[select.selectedIndex].value).toBe("");
    // We don't show the first blank option in the combobox,
    // so we should expect the length to be minus one.
    expect(screen.getAllByRole("option").length).toBe(props.choices.length - 1);
  });

  test("Selected item is revert to display onBlur of input", async () => {
    render(<Select {...props} />);

    await user.type(screen.getByRole("combobox"), props.choices[1].label);
    expect(screen.getByRole("option").textContent).toBe(
      `${props.choices[1].label}, From: ${props.choices[1].organisation}`
    );
    await user.click(screen.getByRole("option"));

    await user.type(
      screen.getByRole("combobox"),
      "{Backspace}{Backspace}{Backspace}"
    );
    expect(screen.getByRole("combobox").value).toBe(
      props.choices[1].label.slice(0, -3)
    );

    await user.tab();
    expect(screen.getByRole("combobox").value).toBe(props.choices[1].label);
    const select = screen.getByTestId(props.data.name);
    expect(select.options[select.selectedIndex].value).toBe(
      props.choices[1].value
    );
  });

  // Errors are displayed
  test("Selected item is revert to display onBlur of input", async () => {
    const err = "I am an error";
    render(<Select {...props} errors={[err]} />);
    expect(screen.getByText(err)).toBeVisible;
  });
});
