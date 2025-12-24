"use client";

import { Listbox, Transition } from "@headlessui/react";
import { Check, ChevronDown } from "lucide-react";
import { Fragment } from "react";

import type { Tenant } from "@/src/types";

export function TenantSwitcher({
  tenants,
  selectedTenant,
  onSelect,
}: {
  tenants: Tenant[];
  selectedTenant: Tenant | null;
  onSelect?: (tenant: Tenant) => void;
}) {
  const disabled = tenants.length === 0 || !onSelect;
  const listboxValue = selectedTenant ?? undefined;
  return (
    <div className="w-72">
      <Listbox
        value={listboxValue}
        onChange={(value) => {
          if (value) onSelect?.(value as Tenant);
        }}
        disabled={disabled}
      >
        <div className="relative mt-1">
          <Listbox.Button className="relative w-full cursor-default rounded-full border border-slate-800 bg-slate-900/60 py-3 pl-5 pr-10 text-left text-sm text-white shadow-sm focus:outline-none">
            <span className="block truncate">
              {selectedTenant ? selectedTenant.name : disabled ? "无可用租户" : "选择租户"}
            </span>
            <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
              <ChevronDown className="h-4 w-4 text-slate-400" aria-hidden="true" />
            </span>
          </Listbox.Button>
          <Transition
            as={Fragment}
            leave="transition ease-in duration-100"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <Listbox.Options className="absolute mt-1 max-h-60 w-full overflow-auto rounded-2xl bg-slate-900/95 py-1 text-sm text-white shadow-lg">
              {tenants.map((tenant) => (
                <Listbox.Option
                  key={tenant.id}
                  className={({ active }) =>
                    `relative cursor-default select-none py-3 pl-5 pr-10 ${
                      active ? "bg-brand-primary/20 text-white" : "text-slate-200"
                    }`
                  }
                  value={tenant}
                >
                  {({ selected }) => (
                    <>
                      <span className={`block truncate ${selected ? "font-medium" : "font-normal"}`}>
                        {tenant.name}
                      </span>
                      {selected ? (
                        <span className="absolute inset-y-0 right-0 flex items-center pr-3 text-brand-secondary">
                          <Check className="h-4 w-4" aria-hidden="true" />
                        </span>
                      ) : null}
                    </>
                  )}
                </Listbox.Option>
              ))}
            </Listbox.Options>
          </Transition>
        </div>
      </Listbox>
    </div>
  );
}
