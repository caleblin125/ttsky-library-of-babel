module babel (
	clk,
	reset,
	charIn,
	setSeed,
	charOut,
	isWriting
);
	reg _sv2v_0;
	input clk;
	input reset;
	input [4:0] charIn;
	input setSeed;
	output wire [4:0] charOut;
	output wire isWriting;
	reg [7:0] counter;
	reg [15:0] state;
	reg [15:0] nextState;
	function [15:0] rng_step;
		input [15:0] state;
		reg [15:0] s;
		begin
			s = state;
			s = s ^ (s << 5);
			s = s + 16'd62179;
			s = s ^ 16'd10208;
			s = s ^ (s << 7);
			rng_step = s;
		end
	endfunction
	always @(*) begin : randgen
		if (_sv2v_0)
			;
		if (setSeed)
			nextState = {state[10:5] + 1'b1, charIn, state[15:11]} ^ (state << 2);
		else
			nextState = rng_step(state);
	end
	wire pageGo;
	assign pageGo = counter != 8'hff;
	always @(posedge clk) begin : registers
		if (!reset) begin
			state <= 27143;
			counter <= 0;
		end
		else if (pageGo) begin
			state <= nextState;
			if (!setSeed)
				counter <= counter + 1;
		end
	end
	assign isWriting = pageGo;
	assign charOut = (pageGo ? state[15:11] : 0);
	initial _sv2v_0 = 0;
endmodule
