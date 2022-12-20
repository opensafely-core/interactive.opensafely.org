import { Field } from "formik";
import React, { Fragment } from "react";
import Combobox from "./Combobox";
import InputFeedback from "./InputFeedback";
import RadioButton from "./RadioButton";
import RadioButtonGroup from "./RadioButtonGroup";

function CodelistSelect({
  codelists,
  errors,
  id,
  setFieldValue,
  touched,
  values,
}) {
  const codelist = `codelist${id}`;
  const codelistType = `codelistType${id}`;
  const codelistTypes = `codelistTypes${id}`;

  return (
    <>
      <h2>Select a codelist</h2>
      <RadioButtonGroup
        className="mb-2"
        id={codelistTypes}
        label="Select a codelist type"
        value={values[codelistType]}
        error={errors[codelistType]}
        touched={touched[codelistType]}
        hideLabel
      >
        {codelists.map((type) => (
          <Field
            component={RadioButton}
            id={type.name.toLowerCase() + id}
            key={type.id + id}
            label={type.name}
            name={codelistType}
            required
            resetOnChange={() => setFieldValue(codelist, {})}
            value={type.name.toLowerCase()}
          />
        ))}
      </RadioButtonGroup>
      {codelists.map((type) => (
        <Fragment key={type.id}>
          {values[codelistType] === type.name.toLowerCase() ? (
            <>
              <Combobox
                choices={type.codelists}
                label="Select a codelist"
                name={codelist}
                setFieldValue={setFieldValue}
                placeholder="Search for a codelist"
                {...(values?.[codelist]?.label && {
                  initialSelectedItem: values[codelist],
                })}
              />
              {touched[codelist] && errors[codelist] && (
                <InputFeedback error={"Select a codelist"} />
              )}
            </>
          ) : null}
        </Fragment>
      ))}
    </>
  );
}

export default CodelistSelect;
