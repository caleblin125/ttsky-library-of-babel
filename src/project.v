/*
 * Copyright (c) 2026 Caleb Lin
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_library_of_babel_caleblin125 (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  babel main(
    .clk(clk),
    .reset(rst_n),
    .charIn(ui_in[4:0]),
    .setSeed(ui_in[5]),
    .charOut(uo_out[4:0]),
    .isWriting(uo_out[5])
  );

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, uio_in,  1'b0};
  assign uo_out[7:6] = 0;
  assign uio_out = 0;
  assign uio_oe  = 0;

endmodule
