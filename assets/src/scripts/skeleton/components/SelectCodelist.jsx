import { Field, useFormikContext } from "formik";
import React, { Fragment } from "react";
import { usePageData } from "../context/page-data-context";
import codelists from "../data/codelists.json";
import { classNames } from "../utils";
import { Combobox } from "./Combobox";

function SelectCodelist({ id }) {
  const codelist = "codelist" + id;
  const codelistType = "codelistType" + id;
  const codelistGroup = "codelistGroup" + id;

  const {
    state: { data },
  } = usePageData();
  const {
    errors,
    setFieldError,
    setFieldTouched,
    setFieldValue,
    touched,
    validateForm,
    values,
  } = useFormikContext();

  const radioButtonChange = ({ id }) => {
    if (id !== values[codelistType]) {
      setFieldValue(codelist, "");
      setFieldTouched(codelist, false);
    }
  };

  const handleSelectedItemChange = (item) => {
    setFieldError(codelist, undefined);
    setFieldValue(codelist, item?.selectedItem || undefined);
    setFieldTouched(codelist, true);
    setTimeout(() => validateForm(), 0);
  };

  return (
    <div role="group" aria-labelledby={codelistGroup}>
      <h2 id={codelistGroup}>Select a codelist</h2>
      <fieldset>
        <legend className="sr-only">Select a codelist type</legend>
        <div className="grid grid-cols-2 gap-2">
          {codelists.map((item) => (
            <label
              key={item.name}
              className={classNames(
                "border rounded-md py-2 px-1 flex items-center justify-center text-sm font-semibold sm:flex-1 cursor-pointer focus:outline-none",
                item.id === values[codelistType]
                  ? "ring-2 ring-oxford-500"
                  : null
              )}
              onClick={() => radioButtonChange({ id: item.id })}
            >
              <Field
                className="sr-only"
                type="radio"
                name={codelistType}
                value={item.id}
              />
              {item.name}
            </label>
          ))}
        </div>
      </fieldset>

      {errors[codelistType] && touched[codelistType] ? (
        <div>{errors[codelistType]}</div>
      ) : null}
      {codelists.map((item) => (
        <Fragment key={item.id}>
          {item.id === values[codelistType] ? (
            <>
              <Combobox
                choices={data}
                data={{
                  choices: "",
                  errors: "",
                  hint: "",
                  id: "",
                  label: "",
                  name: "",
                }}
                errors={[""]}
                handleSelectedItemChange={(item) =>
                  handleSelectedItemChange(item)
                }
                initialSelectedItem={values[codelist]}
              />
              {errors[codelist] && touched[codelist] ? (
                <div>{console.log(errors[codelist])}</div>
              ) : null}
            </>
          ) : null}
        </Fragment>
      ))}
    </div>
  );
}

export default SelectCodelist;
