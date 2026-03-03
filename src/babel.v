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
	wire [15:7] shift3;
	assign shift3 = state << 7;
	always @(*) begin : randgen
		if (_sv2v_0)
			;
		if (setSeed)
			nextState = {state[15:5], charIn} ^ (state << 2);
		else
			nextState = ((state ^ {state[14:2], shift3, state[5:1]}) - shift3) + 1;
	end
	wire pageGo;
	assign pageGo = counter != 8'hff;
	always @(posedge clk) begin : registers
		if (!reset) begin
			state <= 0;
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
