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
	reg [4:0] state;
	reg [4:0] nextState0;
	reg [4:0] nextState1;
	reg [4:0] nextState2;
	always @(*) begin : randgen
		if (_sv2v_0)
			;
		if (setSeed)
			nextState0 = charIn ^ (state << 2);
		else
			nextState0 = state ^ (state << 2);
	end
	wire pageGo;
	assign pageGo = counter != 8'hff;
	always @(posedge clk) begin : registers
		if (!reset) begin
			state <= 0;
			counter <= 0;
			nextState1 <= 0;
			nextState2 <= 0;
		end
		else if (pageGo) begin
			state <= nextState2 + nextState0;
			nextState1 <= nextState0 + 1;
			nextState2 <= nextState0 ^ (nextState1 << 3);
			if (!setSeed)
				counter <= counter + 1;
		end
	end
	assign isWriting = pageGo;
	assign charOut = (pageGo ? state : 0);
	initial _sv2v_0 = 0;
endmodule
